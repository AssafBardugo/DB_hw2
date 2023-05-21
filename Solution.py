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
        conn.execute("DROP TABLE IF EXISTS RamInDisk CASCADE;    \
                      DROP TABLE IF EXISTS PhotoInDisk CASCADE;  \
                      DROP TABLE IF EXISTS DiskTable CASCADE;    \
                      DROP TABLE IF EXISTS RamTable CASCADE;     \
                      DROP TABLE IF EXISTS PhotoTable CASCADE;")
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
    except Exception as e:
        print(e)
        return ReturnValue.ERROR
    finally:
        conn.close() 
    return ReturnValue.OK


def addPhoto(photo: Photo) -> ReturnValue:
    #   INSERT INTO PhotoTable
    #        VALUES (id, description, size);
    query = sql.SQL("INSERT INTO PhotoTable    \
                          VALUES ({id}, {description}, {size});").format(
                            id = sql.Literal(photo.getPhotoID()),
                            description = sql.Literal(photo.getDescription()),
                            size = sql.Literal(photo.getSize()))
    return addItemAUX(query)


def convertToPhotoAUX(result: Connector.ResultSet) -> list[Photo]:
    photos = []
    for i in result.size():
        photos.append(Photo(result[i]['photo_ID'], 
                            result[i]['description'], 
                            result[i]['size']))
    return photos


def getPhotoByID(photoID: int) -> Photo:
    #    SELECT *
    #      FROM PhotoTable
    #     WHERE photo_ID = photoID;

    conn = Connector.DBConnector()
    # If we are here, conn is valid.
    _, result = conn.execute(sql.SQL("SELECT *               \
                                        FROM PhotoTable      \
                                       WHERE photo_ID = {}").format(sql.Literal(photoID)))
    conn.commit()
    conn.close()

    if result.isEmpty():
        return Photo.badPhoto()
    
    # photoID should be unique
    assert(result.size() == 1)

    return convertToPhotoAUX(result)[0]


def deletePhoto(photo: Photo) -> ReturnValue:

    #   DELETE FROM PhotoTable
    #   WHERE photo_ID == this->Photo.__photoID

    #   DELETE FROM PhotoInDisk
    #   WHERE photo_ID == this->Photo.__photoID

    return ReturnValue.OK


def addDisk(disk: Disk) -> ReturnValue:
    #   INSERT INTO DiskTable
    #        VALUES (id, company, speed, free_space, cost);
    query = sql.SQL("INSERT INTO DiskTable  \
                          VALUES ({id}, {company}, {speed}, {free_space}, {cost})").format(
                            id = sql.Literal(disk.getDiskID()),
                            company = sql.Literal(disk.getCompany()),
                            speed = sql.Literal(disk.getSpeed()),
                            free_space = sql.Literal(disk.getFreeSpace()),
                            cost = sql.Literal(disk.getCost()))
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
    #    SELECT *
    #      FROM DiskTable
    #     WHERE disk_ID = diskID;

    conn = Connector.DBConnector()
    _, result = conn.execute(sql.SQL("SELECT *               \
                                        FROM DiskTable       \
                                       WHERE disk_ID = {}").format(sql.Literal(diskID)))
    conn.commit()
    conn.close()

    if result.isEmpty():
        return Disk.badDisk()
    
    # diskID should be unique
    assert(result.size() == 1)

    return convertToDiskAUX(result)[0]


def deleteDisk(diskID: int) -> ReturnValue:
    return ReturnValue.OK


def addRAM(ram: RAM) -> ReturnValue:
    #   INSERT INTO RamTable
    #        VALUES (id, company, size);
    query = sql.SQL("INSERT INTO RamTable   \
                          VALUES ({id}, {company}, {size})").format(
                            id = sql.Literal(ram.getRamID()),
                            company = sql.Literal(ram.getCompany()),
                            size = sql.Literal(ram.getSize()))
    return addItemAUX(query)


def convertToRamAUX(result: Connector.ResultSet) -> list[RAM]:
    rams = []
    for i in result.size():
        rams.append(RAM(result[i]['ram_ID'],
                        result[i]['company'],
                        result[i]['size']))
    return rams


def getRAMByID(ramID: int) -> RAM:
    #    SELECT *
    #      FROM RamTable
    #     WHERE ram_ID = ramID;

    conn = Connector.DBConnector()
    _, result = conn.execute(sql.SQL("SELECT *               \
                                        FROM RamTable        \
                                       WHERE ram_ID = {}").format(sql.Literal(ramID)))
    conn.commit()
    conn.close()

    if result.isEmpty():
        return RAM.badRAM()
    
    # ramID should be unique
    assert(result.size() == 1)

    return convertToRamAUX(result)[0]


def deleteRAM(ramID: int) -> ReturnValue:
    return ReturnValue.OK


def addDiskAndPhoto(disk: Disk, photo: Photo) -> ReturnValue:

    #   add_photo =
    #   "INSERT INTO PhotoTable
    #         VALUES (id, description, size); "

    #   add_disk =
    #   "INSERT INTO DiskTable
    #         VALUES (id, company, speed, free_space, cost);"

    #   execute(add_photo + add_disk)

    return ReturnValue.OK


def addPhotoToDisk(photo: Photo, diskID: int) -> ReturnValue:

    #   save_photo =
    #       INSERT INTO PhotoInDisk
    #       VALUES (disk_ID, photo_ID);

    # If there is not enough 'free_space' on the disk,
    #   an exception should be thrown following the next update query. #

    #   update_disk_space =     # auxUpdateDiskSpaceQuery(-Photo.__size) #
    #       UPDATE DiskTable
    #       SET free_space = free_space - Photo.__size
    #       WHERE disk_ID = this->diskID

    return ReturnValue.OK

def auxUpdateDiskSpaceQuery(extra: int) -> str:
    return "UPDATE DiskTable    \
               SET free_space = free_space + " + str(extra)     \
         + " WHERE disk_ID = this->diskID"

def removePhotoFromDisk(photo: Photo, diskID: int) -> ReturnValue:

    #   try_to_remove =
    #       DELETE FROM PhotoInDisk
    #       WHERE photo_ID = Photo.__photoID AND disk_ID = diskID;

    # In case of success only:
    #   update_disk_space = auxUpdateDiskSpaceQuery(Photo.__size)

    return ReturnValue.OK


def addRAMToDisk(ramID: int, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def removeRAMFromDisk(ramID: int, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def averagePhotosSizeOnDisk(diskID: int) -> float:

    #
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
