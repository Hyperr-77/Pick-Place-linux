import sqlite3
from numpy import ndarray

class Database():
    """Database class that handles all stored data"""
    def __init__(self, database_path: str) -> None:
        """Initialize parameters"""
        self.path = database_path
        self.connection = None
        self.cursor = None

    def _initialize_database(self) -> None:
        """Create tables automatically if they don't exist yet"""
        if self.cursor:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    eps REAL CHECK(eps >= 0 AND eps <= 3),
                    vector BLOB
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bin_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    x REAL,
                    y REAL,
                    cluster_id INTEGER REFERENCES clusters(id)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ui_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prev_image BLOB,
                    full_image BLOB,
                    background_image BLOB,
                    cluster_id INTEGER REFERENCES clusters(id)
                )
            """)

    def __enter__(self) -> sqlite3.Cursor:
        """Open database connection and initialize the tables"""
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._initialize_database()
        return self.cursor

    def __exit__(self, exception_type, exception_value, exception_traceback) -> bool | None:
        """Handle transactions and close the connection"""
        if self.connection and self.cursor:
            if exception_type is not None:
                print(f"Error detected when closing database: {exception_value}. Rolling back changes.")
                self.connection.rollback()
            else:
                self.connection.commit()

            self.cursor.close()
            self.connection.close()
        return False
    
    def add_cluster(self, vector: bytes, eps: float) -> int:
        """Add a new cluster to the database, returns the new cluster id"""
        with self as cursor:
            cursor.execute("INSERT INTO clusters (eps, vector) VALUES (?, ?)", (eps, vector))
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def update_cluster(self, cluster_id: int, eps: float) -> bool:
        """Change eps value of cluster with id: (cluster_id)"""
        with self as cursor:
            cursor.execute("UPDATE clusters SET eps = ? WHERE id = ?", (eps, cluster_id,))
            return cursor.rowcount > 0

    def remove_cluster(self, cluster_id: int) -> bool:
        """Remove a cluster and its associated bins and UI images."""
        with self as cursor:
            cursor.execute("DELETE FROM bin_data WHERE cluster_id = ?", (cluster_id,))
            cursor.execute("DELETE FROM ui_data WHERE cluster_id = ?", (cluster_id,))
            cursor.execute("DELETE FROM clusters WHERE id = ?", (cluster_id,))
            return cursor.rowcount > 0

    def get_cluster(self, cluster_id: int) -> sqlite3.Row:
        """Get cluster with id: (cluster_id)"""
        with self as cursor:
            cursor.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,))
            return cursor.fetchone()

    def get_last_cluster_id(self) -> int:
        """Get the id value of the last added cluster (amount of clusters in the database)"""
        with self as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM clusters")
            return cursor.fetchone()["count"]

    def stream_clusters(self):
        """Stream all clusters in the database one by one"""
        with self as cursor:
            cursor.execute("SELECT * FROM clusters")
            for row in cursor:
                yield row

    def add_bin(self, center_x, center_y) -> int:
        """Add a bin to the database, returns the new bin id"""
        with self as cursor:
            cursor.execute("INSERT INTO bin_data (x, y) VALUES (?, ?)", (center_x, center_y))
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def remove_bin(self, bin_id: int) -> bool:
        """Remove a bin from the database with id (bin_id)"""
        with self as cursor:
            cursor.execute("DELETE FROM bin_data WHERE id = ?", (bin_id,))
            return cursor.rowcount > 0

    def get_bin(self, cluster_id: int) -> sqlite3.Row:
        """Get the bin that holds the cluster with id (id), holds an id, the bin position (center_x, center_y) in mm and cluster_id"""
        with self as cursor:
            cursor.execute("SELECT * FROM bin_data WHERE cluster_id = ?", (cluster_id,))
            return cursor.fetchone()

    def subscribe_bin(self, cluster_id: int) -> int:
        """Subscribe a cluster to a unassigned bin"""
        with self as cursor:
            cursor.execute("SELECT id FROM bin_data WHERE cluster_id IS NULL")
            bin_row = cursor.fetchone()
            if bin_row is None:
                return 0
            cursor.execute("UPDATE bin_data SET cluster_id = ? WHERE id = ?", (cluster_id, bin_row["id"]))
            return bin_row["id"] if cursor.rowcount > 0 else 0

    def unsubscribe_bin(self, cluster_id: int) -> bool:
        """Unsubscribe a cluster from a bin"""
        with self as cursor:
            cursor.execute("SELECT id FROM bin_data WHERE cluster_id = ?", (cluster_id,))
            bin_row = cursor.fetchone()
            if bin_row is None:
                return False
            cursor.execute("UPDATE bin_data SET cluster_id = NULL WHERE id = ?", (bin_row["id"],))
            return cursor.rowcount > 0

    def add_ui(self, cluster_id: int, prev_image, full_image, background_image) -> int:
        """Add a new UI data object to the database, returns the new UI data id"""
        with self as cursor:
            cursor.execute(
                """
                INSERT INTO ui_data (
                    cluster_id, prev_image, full_image, background_image
                ) VALUES (?, ?, ?, ?)
                """,
                (cluster_id, prev_image, full_image, background_image),
            )
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def remove_ui(self, ui_id: int) -> bool:
        """Remove UI data object with id: (ui_id)"""
        with self as cursor:
            cursor.execute("DELETE FROM ui_data WHERE id = ?", (ui_id,))
            return cursor.rowcount > 0

    def get_ui(self, ui_id: int) -> sqlite3.Row:
        """Get UI data object with id: (ui_id)"""
        with self as cursor:
            cursor.execute("SELECT * FROM ui_data WHERE id = ?", (ui_id,))
            return cursor.fetchone()

    def stream_ui(self):
        """Stream all UI data objects in the database one by one"""
        with self as cursor:
            cursor.execute("SELECT * FROM ui_data ORDER BY cluster_id, id")
            for row in cursor:
                yield row