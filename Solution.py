from typing import List
import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Photo import Photo
from Business.RAM import RAM
from Business.Disk import Disk
from psycopg2 import sql


def createTables():
    PhotoTable = "CREATE TABLE PhotoTable                                               \
                    (photo_ID       INTEGER     CHECK(photo_ID > 0)     PRIMARY KEY,    \
                     description    TEXT                                NOT NULL,       \
                     size           INTEGER     CHECK(size >= 0)        NOT NULL); "

    RamTable = "CREATE TABLE RamTable                                                   \
                   (ram_ID         INTEGER     CHECK(ram_ID > 0)       PRIMARY KEY,     \
                    company        TEXT                                NOT NULL,        \
                    size           INTEGER     CHECK(size > 0)         NOT NULL); "

    DiskTable = "CREATE TABLE DiskTable                                                 \
                   (disk_ID        INTEGER     CHECK(disk_ID > 0)      PRIMARY KEY,     \
                    company        TEXT                                NOT NULL,        \
                    speed          INTEGER     CHECK(speed > 0)        NOT NULL,        \
                    free_space     INTEGER     CHECK(free_space >= 0)  NOT NULL,        \
                    cost           INTEGER     CHECK(cost > 0)         NOT NULL); "

    PhotoInDisk = "CREATE TABLE PhotoInDisk                                             \
                   (disk_ID        INTEGER     REFERENCES DiskTable,                    \
                    photo_ID       INTEGER     REFERENCES PhotoTable,                   \
                    UNIQUE(disk_ID, photo_ID)); "

    RamInDisk = "CREATE TABLE RamInDisk                                                 \
                   (disk_ID        INTEGER     REFERENCES DiskTable,                    \
                    ram_ID         INTEGER     REFERENCES RAMTable,                     \
                    UNIQUE(disk_ID, ram_ID)); "

    """
    # VIEWs:
    # for getPhotosCanBeAddedToDisk:
    DiskBySpaceVIEW = "CREATE VIEW DiskBySpaceVIEW AS                                   \
                                SELECT disk_ID, free_space                              \
                                  FROM DiskTable; "

    PhotoBySizeVIEW = "CREATE VIEW PhotoBySizeVIEW AS                                   \
                                SELECT photo_ID, size                                   \
                                  FROM PhotoTable; "

    PhotosCanBeAddedVIEW = "CREATE VIEW PhotosCanBeAddedVIEW AS                         \
                                SELECT DiskBySpaceVIEW.disk_ID,                         \
                                       PhotoBySizeVIEW.photo_ID                         \
                                  FROM DiskBySpaceVIEW, PhotoBySizeVIEW                 \
                                 WHERE DiskBySpaceVIEW.free_space >= PhotoBySizeVIEW.size; "

    # for getPhotosCanBeAddedToDiskAndRAM:
    DiskBySumRamVIEW = "CREATE VIEW DiskBySumRamVIEW AS                                 \
                                SELECT disk_ID, SUM(size) AS sum_ram                    \
                                  FROM RamDataVIEW                                      \
                                 GROUP BY disk_ID; "

    DiskBySpaceAndRamVIEW = "CREATE VIEW DiskBySpaceAndRamVIEW AS                       \
                                SELECT DiskBySpaceVIEW.disk_ID,                         \
                                       DiskBySpaceVIEW.free_space,                      \
                                       DiskBySumRamVIEW.sum_ram                         \
                                  FROM DiskBySpaceVIEW,                                 \
                                       DiskBySumRamVIEW                                 \
                                 WHERE DiskBySpaceVIEW.disk_ID = DiskBySumRamVIEW.disk_ID; "

    CanBeAddedToDiskAndRamVIEW = "CREATE VIEW CanBeAddedToDiskAndRamVIEW AS             \
                                SELECT DiskBySpaceAndRamVIEW.disk_ID,                   \
                                       PhotoBySizeVIEW.photo_ID                         \
                                  FROM DiskBySpaceAndRamVIEW,                           \
                                       PhotoBySizeVIEW                                  \
                                 WHERE DiskBySpaceAndRamVIEW.free_space >= PhotoBySizeVIEW.size     \
                                   AND DiskBySpaceAndRamVIEW.sum_ram >= PhotoBySizeVIEW.size; "
    """
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(PhotoTable + RamTable + DiskTable + PhotoInDisk + RamInDisk)
                  #   DiskBySpaceVIEW + PhotoBySizeVIEW + PhotosCanBeAddedVIEW +
                  #   DiskBySumRamVIEW + DiskBySpaceAndRamVIEW + CanBeAddedToDiskAndRamVIEW)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def clearTables():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DELETE FROM RamInDisk;    \
                      DELETE FROM PhotoInDisk;  \
                      DELETE FROM DiskTable;    \
                      DELETE FROM RamTable;     \
                      DELETE FROM PhotoTable;")
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def dropTables():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DROP TABLE IF EXISTS RamInDisk    CASCADE;    \
                      DROP TABLE IF EXISTS PhotoInDisk  CASCADE;    \
                      DROP TABLE IF EXISTS DiskTable    CASCADE;    \
                      DROP TABLE IF EXISTS RamTable     CASCADE;    \
                      DROP TABLE IF EXISTS PhotoTable   CASCADE;")
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def addItemAUX(query: sql.Composed) -> ReturnValue:
    # Generic function to add an item to a table, 
    #   just for avoiding code duplication.
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(query)
        conn.commit()
    except (DatabaseException.NOT_NULL_VIOLATION, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def addPhoto(photo: Photo) -> ReturnValue:
    query = sql.SQL(
        "INSERT INTO PhotoTable    \
         VALUES ({id}, {description}, {size});"
    ).format(
        id = sql.Literal(photo.getPhotoID()),
        description = sql.Literal(photo.getDescription()),
        size = sql.Literal(photo.getSize())
    )
    return addItemAUX(query)


def convertToPhotoAUX(result: Connector.ResultSet) -> list[Photo]:
    photos = []
    for i in result.size():
        photos.append(Photo(result[i]['photo_ID'], 
                            result[i]['description'], 
                            result[i]['size']))
    return photos


def getPhotoByID(photoID: int) -> Photo:
    conn = Connector.DBConnector()
    # If we are here, conn is valid.
    _, result = conn.execute(
        sql.SQL(
            "SELECT *               \
               FROM PhotoTable      \
              WHERE photo_ID = {photo_id};"
        ).format(photo_id = sql.Literal(photoID))
    )
    conn.commit()
    conn.close()

    if result.isEmpty():
        return Photo.badPhoto()
    
    # photoID should be unique
    assert(result.size() == 1)
    res = convertToPhotoAUX(result)
    return res[0]


def deletePhoto(photo: Photo) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "UPDATE DiskTable                                   \
                    SET free_space = free_space + {size}            \
                  WHERE disk_ID                                     \
                     IN (SELECT disk_ID                             \
                           FROM PhotoInDisk                         \
                          WHERE photo_ID = {photo_id});             \
                                                                    \
                DELETE FROM PhotoInDisk, PhotoTable                 \
                 WHERE photo_ID = {photo_id};"
            ).format(
                size = sql.Literal(photo.getSize()), 
                photo_id = sql.Literal(photo.getPhotoID())
            )
        )
        conn.commit()
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def addDisk(disk: Disk) -> ReturnValue:
    query = sql.SQL(
        "INSERT INTO DiskTable  \
         VALUES ({id}, {company}, {speed}, {free_space}, {cost});"
    ).format(
        id = sql.Literal(disk.getDiskID()),
        company = sql.Literal(disk.getCompany()),
        speed = sql.Literal(disk.getSpeed()),
        free_space = sql.Literal(disk.getFreeSpace()),
        cost = sql.Literal(disk.getCost())
    )
    return addItemAUX(query)


def convertToDiskAUX(result: Connector.ResultSet) -> list[Disk]:
    disks = []
    for i in result.size():
        disks.append(Disk(result[i]['disk_ID'],
                          result[i]['company'],
                          result[i]['speed'],
                          result[i]['free_space'],
                          result[i]['cost']))
    return disks


def getDiskByID(diskID: int) -> Disk:
    conn = Connector.DBConnector()
    _, result = conn.execute(
        sql.SQL(
            "SELECT *               \
               FROM DiskTable       \
              WHERE disk_ID = {};"
        ).format(sql.Literal(diskID))
    )
    conn.commit()
    conn.close()

    if result.isEmpty():
        return Disk.badDisk()
    
    # diskID should be unique
    assert(result.size() == 1)
    return convertToDiskAUX(result)[0]


def deleteDisk(diskID: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM PhotoInDisk,   \
                             RamInDisk,     \
                             DiskTable      \
                  WHERE disk_ID = {disk_id};"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK if rows_effected > 0 else ReturnValue.NOT_EXISTS


def addRAM(ram: RAM) -> ReturnValue:
    query = sql.SQL(
        "INSERT INTO RamTable   \
         VALUES ({id}, {company}, {size})"
    ).format(
        id = sql.Literal(ram.getRamID()),
        company = sql.Literal(ram.getCompany()),
        size = sql.Literal(ram.getSize())
    )
    return addItemAUX(query)


def convertToRamAUX(result: Connector.ResultSet) -> list[RAM]:
    rams = []
    for i in result.size():
        rams.append(RAM(result[i]['ram_ID'],
                        result[i]['company'],
                        result[i]['size']))
    return rams


def getRAMByID(ramID: int) -> RAM:
    conn = Connector.DBConnector()
    _, result = conn.execute(
        sql.SQL(
            "SELECT *               \
               FROM RamTable        \
              WHERE ram_ID = {};"
        ).format(sql.Literal(ramID))
    )
    conn.commit()
    conn.close()

    if result.isEmpty():
        return RAM.badRAM()
    
    # ramID should be unique
    assert(result.size() == 1)
    return convertToRamAUX(result)[0]


def deleteRAM(ramID: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM RamInDisk,     \
                             RamTable       \
                  WHERE ram_ID = {ram_id};"
            ).format(
                ram_id = sql.Literal(ramID)
            )
        )
        conn.commit()
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK if rows_effected > 0 else ReturnValue.NOT_EXISTS


def addDiskAndPhoto(disk: Disk, photo: Photo) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO PhotoTable                             \
                      VALUES ({photo_id}, {description}, {size});   \
                 INSERT INTO DiskTable                              \
                      VALUES ({disk_id}, {company}, {speed}, {free_space}, {cost});"
            ).format(
                photo_id = sql.Literal(photo.getPhotoID()),
                description = sql.Literal(photo.getDescription()),
                size = sql.Literal(photo.getSize()), 
                disk_id = sql.Literal(disk.getDiskID()),
                company = sql.Literal(disk.getCompany()),
                speed = sql.Literal(disk.getSpeed()),
                free_space = sql.Literal(disk.getFreeSpace()),
                cost = sql.Literal(disk.getCost())
            )
        )
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        return ReturnValue.ERROR
    else:
        conn.commit()
    finally:
        conn.close()
    return ReturnValue.OK


### Basic API ###
def addPhotoToDisk(photo: Photo, diskID: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "UPDATE DiskTable                               \
                    SET free_space = free_space - {photo_size}  \
                  WHERE disk_ID = {disk_id};                    \
                                                                \
                INSERT INTO PhotoInDisk                         \
                VALUES ({disk_id}, {photo_id});"
            ).format(
                photo_size = sql.Literal(photo.getPhotoID()),
                disk_id = sql.Literal(diskID),
                photo_id = sql.Literal(photo.getPhotoID())
            )
        )
    except DatabaseException.FOREIGN_KEY_VIOLATION: 
        # Thrown by REFERENCES in PhotoInDisk
        conn.rollback()
        return ReturnValue.NOT_EXISTS
    except DatabaseException.UNIQUE_VIOLATION:
        # Thrown by UNIQUE in PhotoInDisk
        conn.rollback()
        return ReturnValue.ALREADY_EXISTS
    except DatabaseException.CHECK_VIOLATION:
        # Thrown by CHECK(free_space >= 0) in DiskTable
        conn.rollback()
        return ReturnValue.BAD_PARAMS
    except Exception:
        return ReturnValue.ERROR
    else:
        conn.commit()
    finally:
        conn.close()
    return ReturnValue.OK


def removePhotoFromDisk(photo: Photo, diskID: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "UPDATE DiskTable                                   \
                    SET free_space = free_space + {photo_size}      \
                  WHERE disk_ID IN (SELECT disk_ID                  \
                                      FROM PhotoInDisk              \
                                     WHERE disk_ID = {disk_id}      \
                                       AND photo_ID = {photo_id});  \
                                                                    \
                DELETE FROM PhotoInDisk                             \
                 WHERE disk_ID = {disk_id}                          \
                   AND photo_ID = {photo_id};"
            ).format(
                photo_size = sql.Literal(photo.getSize()),
                disk_id = sql.Literal(diskID),
                photo_id = sql.Literal(photo.getPhotoID())
            )
        )
        conn.commit()
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def addRAMToDisk(ramID: int, diskID: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO RamInDisk  \
                 VALUES ({disk_id}, {ram_id});"
            ).format(
                disk_id = sql.Literal(diskID),
                ram_id = sql.Literal(ramID)
            )
        )
    except DatabaseException.FOREIGN_KEY_VIOLATION: 
        # Thrown by REFERENCES in RamInDisk
        return ReturnValue.NOT_EXISTS
    except DatabaseException.UNIQUE_VIOLATION:
        # Thrown by UNIQUE in RamInDisk
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        return ReturnValue.ERROR
    else:
        conn.commit()
    finally:
        conn.close()
    return ReturnValue.OK


def removeRAMFromDisk(ramID: int, diskID: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM RamInDisk  \
                  WHERE disk_ID = {disk_id} AND ram_ID = {ram_id};"
            ).format(
                disk_id = sql.Literal(diskID),
                ram_id = sql.Literal(ramID)
            )
        )
        conn.commit()
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK if rows_effected > 0 else ReturnValue.NOT_EXISTS


def averagePhotosSizeOnDisk(diskID: int) -> float:
    return 0


def getTotalRamOnDisk(diskID: int) -> int:
    return 0


def getCostForDescription(description: str) -> int:
    return 0


def getPhotosCanBeAddedToDisk(diskID: int) -> List[int]:

    #     SELECT photo_ID
    #       FROM PhotosCanBeAddedVIEW
    #      WHERE disk_ID = diskID
    #   ORDER BY photo_ID
    #      LIMIT 5

    return []


def getPhotosCanBeAddedToDiskAndRAM(diskID: int) -> List[int]:

    #     SELECT photo_ID
    #       FROM CanBeAddedToDiskAndRamVIEW
    #      WHERE disk_ID = diskID
    #   ORDER BY photo_ID   # Note: The list should be ordered by IDs in *ascending* order. #
    #      LIMIT 5

    return []


def isCompanyExclusive(diskID: int) -> bool:

    # Use VIEWs.

    return True


def isDiskContainingAtLeastNumExists(description: str, num: int) -> bool:
    return True


def getDisksContainingTheMostData() -> List[int]:
    return []


def getConflictingDisks() -> List[int]:

    return []


def mostAvailableDisks() -> List[int]:
    return []


def getClosePhotos(photoID: int) -> List[int]:
    return []
