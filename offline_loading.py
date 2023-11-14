import os
import time
import sqlite3
import threading
import requests
import sys
import math
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
        self.number_of_threads = 50
        self.stop_threads_flag = False  # Flag to signal threads to stop

    def start_threads(self):
        for thread in self.thread_pool:
            thread.start()

    def stop_threads(self):
        self.stop_threads_flag = True

    def print_loaded_sections(self):
        # connect to database
        db_connection = sqlite3.connect(self.db_path)
        db_cursor = db_connection.cursor()

        print("[save_offline_tiles] The following sections are in the database:")

        db_cursor.execute("SELECT * FROM sections")
        for section in db_cursor.fetchall():
            print(section)

        print("", end="\n\n")

    def save_offline_tiles_thread(self):
        db_connection = sqlite3.connect(self.db_path, timeout=10)
        db_cursor = db_connection.cursor()

        while not self.stop_threads_flag:  # Check the stop_threads_flag attribute

            self.lock.acquire()
            if len(self.task_queue) > 0:
                task = self.task_queue.pop()
                self.lock.release()
                zoom, x, y = task[0], task[1], task[2]

                print(f"[Thread] Downloading tile: Zoom={zoom}, X={x}, Y={y}")

                check_existence_cmd = f"""SELECT t.zoom, t.x, t.y FROM tiles t WHERE t.zoom=? AND t.x=? AND t.y=? AND server=?;"""
                try:
                    db_cursor.execute(check_existence_cmd, (zoom, x, y, self.tile_server))
                except sqlite3.OperationalError as oe:
                    print(f"[Thread] SQLite Operational Error: {oe}")
                    self.lock.acquire()
                    self.task_queue.append(task)
                    self.lock.release()
                    continue

                result = db_cursor.fetchall()
                if len(result) == 0:
                    try:
                        url = self.tile_server.replace("{x}", str(x)).replace("{y}", str(y)).replace("{z}", str(zoom))
                        image_data = requests.get(url, stream=True, headers={"User-Agent": "TkinterMapView"}).content

                        print(f"[Thread] Tile downloaded successfully: Zoom={zoom}, X={x}, Y={y}")

                        self.lock.acquire()
                        self.result_queue.append((zoom, x, y, self.tile_server, image_data))
                        self.lock.release()

                    except sqlite3.OperationalError as oe:
                        print(f"[Thread] SQLite Operational Error: {oe}")
                        self.lock.acquire()
                        self.task_queue.append(task)  # re-append task to task_queue
                        self.lock.release()

                    except UnidentifiedImageError:
                        print(f"[Thread] UnidentifiedImageError for tile: Zoom={zoom}, X={x}, Y={y}")
                        self.lock.acquire()
                        self.result_queue.append((zoom, x, y, self.tile_server, None))
                        self.lock.release()

                    except Exception as err:
                        print(f"[Thread] Error downloading tile: Zoom={zoom}, X={x}, Y={y}, Error: {str(err)}")
                        self.lock.acquire()
                        self.task_queue.append(task)
                        self.lock.release()
                else:
                    print(f"[Thread] Tile already exists in the database: Zoom={zoom}, X={x}, Y={y}")
                    self.lock.acquire()
                    self.result_queue.append((zoom, x, y, self.tile_server, None))
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

        # create threads
        for i in range(self.number_of_threads):
            thread = threading.Thread(daemon=True, target=self.save_offline_tiles_thread, args=())
            self.thread_pool.append(thread)

        # start threads
        self.start_threads()

        # loop through all zoom levels
        for zoom in range(round(zoom_a), round(zoom_b + 1)):
            upper_left_tile_pos = decimal_to_osm(*position_a, zoom)
            lower_right_tile_pos = decimal_to_osm(*position_b, zoom)

            self.lock.acquire()
            for x in range(math.floor(upper_left_tile_pos[0]), math.ceil(lower_right_tile_pos[0]) + 1):
                for y in range(math.floor(upper_left_tile_pos[1]), math.ceil(lower_right_tile_pos[1]) + 1):
                    self.task_queue.append((zoom, x, y))
            number_of_tasks = len(self.task_queue)
            self.lock.release()

            print(f"[save_offline_tiles] zoom: {zoom:<2}  tiles: {number_of_tasks:<8}  storage: {math.ceil(number_of_tasks * 8 / 1024):>6} MB", end="")
            print(f"  progress: ", end="")

            result_counter = 0
            loading_bar_length = 0
            while result_counter < number_of_tasks:

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

                # update loading bar to current progress (percent)
                percent = result_counter / number_of_tasks
                length = round(percent * 30)
                while length > loading_bar_length:
                    print("█", end="")
                    loading_bar_length += 1

            print(f" {result_counter:>8} tiles loaded")

        print("", end="\n\n")

        # insert loading section in the database
        db_cursor.execute(f"INSERT INTO sections (position_a, position_b, zoom_a, zoom_b, server) VALUES (?, ?, ?, ?, ?);",
                          (str(position_a), str(position_b), zoom_a, zoom_b, self.tile_server))
        db_connection.commit()

        db_connection.close()
        self.stop_threads()  # Ensure threads are stopped when download is complete
        return

# # Example Usage
# loader = OfflineLoader()
# loader.save_offline_tiles((0, 0), (85.05112878, 180), 0, 15)
