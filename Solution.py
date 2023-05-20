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
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(PhotoTable + RamTable + DiskTable + PhotoInDisk + RamInDisk +
                     DiskBySpaceVIEW + PhotoBySizeVIEW + PhotosCanBeAddedVIEW +
                     DiskBySumRamVIEW + DiskBySpaceAndRamVIEW + CanBeAddedToDiskAndRamVIEW)
        conn.commit()
    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        conn.close()


def clearTables():
    pass


def dropTables():
    pass


def addPhoto(photo: Photo) -> ReturnValue:

    #   INSERT INTO PhotoTable
    #        VALUES (id, description, size);

    return ReturnValue.OK


def getPhotoByID(photoID: int) -> Photo:

    #    SELECT *
    #      FROM PhotoTable
    #     WHERE photo_ID == this->photoID

    return Photo()


def deletePhoto(photo: Photo) -> ReturnValue:

    #   DELETE FROM PhotoTable
    #   WHERE photo_ID == this->Photo.__photoID

    #   DELETE FROM PhotoInDisk
    #   WHERE photo_ID == this->Photo.__photoID

    return ReturnValue.OK


def addDisk(disk: Disk) -> ReturnValue:
    return ReturnValue.OK


def getDiskByID(diskID: int) -> Disk:
    return Disk()


def deleteDisk(diskID: int) -> ReturnValue:
    return ReturnValue.OK


def addRAM(ram: RAM) -> ReturnValue:
    return ReturnValue.OK


def getRAMByID(ramID: int) -> RAM:
    return RAM()


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
