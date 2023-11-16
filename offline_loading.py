import os
import time
import sqlite3
import threading
import requests
import sys
import math
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, UnidentifiedImageError

from utility_functions import decimal_to_osm, osm_to_decimal

class OfflineLoader:
    def __init__(self, path=None, tile_server=None, max_zoom=19):
        if path is None:
            self.db_path = os.path.join(os.path.abspath(os.getcwd()), "tiles.db")
        else:
            self.db_path = path

        if tile_server is None:
            self.tile_server = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
        else:
            self.tile_server = tile_server

        self.max_zoom = max_zoom
        self.task_queue = []
        self.result_queue = []
        self.thread_pool = []
        self.lock = threading.Lock()
        self.number_of_threads = 30

    def tile_exists(self, zoom, x, y):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tiles WHERE zoom=? AND x=? AND y=?", (zoom, x, y))
            count = cursor.fetchone()[0]
            return count > 0


    def start_threads(self):
        for thread in self.thread_pool:
            print(f"[Main] Starting thread: {thread.name}")
            thread.start()

    def stop_threads(self):
        for thread in self.thread_pool:
            thread.join()

    def print_loaded_sections(self):
        # connect to database
        db_connection = sqlite3.connect(self.db_path)
        db_cursor = db_connection.cursor()

        print("[save_offline_tiles] The following sections are in the database:")

        db_cursor.execute("SELECT * FROM sections")
        for section in db_cursor.fetchall():
            print(section)

        print("", end="\n\n")

    def save_offline_tiles_thread(self, stop_event):
        db_connection = sqlite3.connect(self.db_path)
        db_cursor = db_connection.cursor()

        while not stop_event.is_set():  # Check the stop_threads_flag attribute

            self.lock.acquire()
            if len(self.task_queue) > 0:
                print("[Thread] Task queue before processing:", self.task_queue)
                task = self.task_queue.pop()
                print("[Thread] Task queue after processing:", self.task_queue)
                self.lock.release()
                zoom, x, y = task[0], task[1], task[2]

                print(f"[Thread] Downloading tile: Zoom={zoom}, X={x}, Y={y}")

                check_existence_cmd = """SELECT 1 FROM tiles t WHERE t.zoom=? AND t.x=? AND t.y=? AND server=? LIMIT 1;"""
                try:
                    url = self.tile_server.replace("{x}", str(x)).replace("{y}", str(y)).replace("{z}", str(zoom))
                    print(f"[Thread] Downloading tile: Zoom={zoom}, X={x}, Y={y}, URL={url}")

                    image_data = requests.get(url, stream=True, headers={"User-Agent": "TkinterMapView"}).content
                    print(f"[Thread] Tile downloaded successfully: Zoom={zoom}, X={x}, Y={y}")

                    self.lock.acquire()

                    # Check if the record already exists
                    existing_record = db_cursor.execute(check_existence_cmd, (zoom, x, y, self.tile_server)).fetchone()
                    if existing_record is None:
                        self.result_queue.append((zoom, x, y, self.tile_server, image_data))
                        insert_tile_cmd = """INSERT INTO tiles (zoom, x, y, server, tile_image) VALUES (?, ?, ?, ?, ?);"""
                        
                        print(f"[Thread] Inserting tile into database: Zoom={zoom}, X={x}, Y={y}")
                        
                        db_cursor.execute(insert_tile_cmd, (zoom, x, y, self.tile_server, image_data))
                        db_connection.commit()
                        print(f"[Thread] Tile inserted into database: Zoom={zoom}, X={x}, Y={y}")
                    
                    self.lock.release()

                except (sqlite3.OperationalError, UnidentifiedImageError) as e:
                    print(f"[Thread] Error: {e}")
                    self.lock.acquire()
                    self.task_queue.append(task)
                    self.lock.release()

                except Exception as e:
                    print(f"[Thread] Error downloading tile: Zoom={zoom}, X={x}, Y={y}, Error: {str(e)}")
                    self.lock.acquire()
                    self.task_queue.append(task)
                    self.lock.release()

            else:
                self.lock.release()

            time.sleep(0.01)

        db_connection.close()


    def save_offline_tiles(self, position_a, position_b, zoom_a, zoom_b):
        # connect to database
        db_connection = sqlite3.connect(self.db_path)
        db_cursor = db_connection.cursor()

        # create tables if they do not exist
        create_server_table = """CREATE TABLE IF NOT EXISTS server (
                                        url VARCHAR(300) PRIMARY KEY NOT NULL,
                                        max_zoom INTEGER NOT NULL);"""

        create_tiles_table = """CREATE TABLE IF NOT EXISTS tiles (
                                        zoom INTEGER NOT NULL,
                                        x INTEGER NOT NULL,
                                        y INTEGER NOT NULL,
                                        server VARCHAR(300) NOT NULL,
                                        tile_image BLOB NOT NULL,
                                        CONSTRAINT fk_server FOREIGN KEY (server) REFERENCES server (url),
                                        CONSTRAINT pk_tiles PRIMARY KEY (zoom, x, y, server));"""

        create_sections_table = """CREATE TABLE IF NOT EXISTS sections (
                                            position_a VARCHAR(100) NOT NULL,
                                            position_b VARCHAR(100) NOT NULL,
                                            zoom_a INTEGER NOT NULL,
                                            zoom_b INTEGER NOT NULL,
                                            server VARCHAR(300) NOT NULL,
                                            CONSTRAINT fk_server FOREIGN KEY (server) REFERENCES server (url),
                                            CONSTRAINT pk_tiles PRIMARY KEY (position_a, position_b, zoom_a, zoom_b, server));"""

        db_cursor.execute(create_server_table)
        db_cursor.execute(create_tiles_table)
        db_cursor.execute(create_sections_table)
        db_connection.commit()

        # check if section is already in the database
        db_cursor.execute("SELECT * FROM sections s WHERE s.position_a=? AND s.position_b=? AND s.zoom_a=? AND s.zoom_b=? AND server=?;",
                          (str(position_a), str(position_b), zoom_a, zoom_b, self.tile_server))
        if len(db_cursor.fetchall()) != 0:
            print("[save_offline_tiles] Section is already in the database", end="\n\n")
            db_connection.close()
            return

        # insert tile_server if not in the database
        db_cursor.execute(f"SELECT * FROM server s WHERE s.url='{self.tile_server}';")
        if len(db_cursor.fetchall()) == 0:
            db_cursor.execute(f"INSERT INTO server (url, max_zoom) VALUES (?, ?);", (self.tile_server, self.max_zoom))
            db_connection.commit()

        # create threads with an event to signal stopping
        stop_event = threading.Event()
        for i in range(self.number_of_threads):
            thread = threading.Thread(daemon=True, target=self.save_offline_tiles_thread, args=(stop_event,))
            self.thread_pool.append(thread)

        # start threads
        self.start_threads()

        # loop through all zoom levels
        for zoom in range(round(zoom_a), round(zoom_b + 1)):
            upper_left_tile_pos = decimal_to_osm(*position_a, zoom)
            lower_right_tile_pos = decimal_to_osm(*position_b, zoom)

            self.lock.acquire()
            number_of_tasks = 0  # Move the task count calculation after acquiring the lock
            for x in range(2 ** zoom):
                for y in range(2 ** zoom):
                    self.task_queue.append((zoom, x, y))
                    number_of_tasks += 1
            self.lock.release()

            print(f"[save_offline_tiles] zoom: {zoom:<2}  tiles: {number_of_tasks:<8}  storage: {math.ceil(number_of_tasks * 8 / 1024):>6} MB", end="")
            print(f"  progress: ", end="")

            # check the task queue after it's populated
            print(f"[save_offline_tiles] Task queue after populating: {self.task_queue}")

            result_counter = 0
            loading_bar_length = 0
            while result_counter < number_of_tasks or len(self.task_queue) > 0:
                self.lock.acquire()
                if len(self.result_queue) > 0:
                    loading_result = self.result_queue.pop()
                    self.lock.release()
                    result_counter += 1

                    if loading_result[-1] is not None:
                        insert_tile_cmd = """INSERT INTO tiles (zoom, x, y, server, tile_image) VALUES (?, ?, ?, ?, ?);"""
                        db_cursor.execute(insert_tile_cmd, loading_result)
                        db_connection.commit()
                else:
                    self.lock.release()

                # Update loading bar to current progress (percent)
                percent = result_counter / number_of_tasks
                length = round(percent * 30)
                while length > loading_bar_length:
                    print("█", end="")
                    loading_bar_length += 1

            print(f" {result_counter} tiles loaded")

        print("", end="\n\n")

        # Wait for all threads to finish before closing the database connection
        self.stop_threads()  # Stop threads after download is complete
        stop_event.set()  # Set the stop event to signal threads to stop
        db_cursor.execute(f"INSERT INTO sections (position_a, position_b, zoom_a, zoom_b, server) VALUES (?, ?, ?, ?, ?);",
                        (str(position_a), str(position_b), zoom_a, zoom_b, self.tile_server))
        db_connection.commit()
        db_connection.close()
        return

# # Example Usage
# loader = OfflineLoader()
# loader.save_offline_tiles((0, 0), (85.05112878, 180), 0, 15)
