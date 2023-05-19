from typing import List
import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Photo import Photo
from Business.RAM import RAM
from Business.Disk import Disk
from psycopg2 import sql


def createTables():
    #   CREATE TABLE PhotoTable    (photo_ID       INTEGER     CHECK(photo_ID > 0)     PRIMARY KEY,
    #                               description    TEXT                                NOT NULL,
    #                               size           INTEGER     CHECK(size >= 0)        NOT NULL);

    #   CREATE TABLE RAMTable      (ram_ID         INTEGER     CHECK(ram_ID > 0)       PRIMARY KEY,
    #                               company        TEXT                                NOT NULL,
    #                               size           INTEGER     CHECK(size > 0)         NOT NULL);

    #   CREATE TABLE DiskTable     (disk_ID        INTEGER     CHECK(disk_ID > 0)      PRIMARY KEY,
    #                               company        TEXT                                NOT NULL,
    #                               speed          INTEGER     CHECK(speed > 0)        NOT NULL,
    #                               free_space     INTEGER     CHECK(free_space >= 0)  NOT NULL,
    #                               cost           INTEGER     CHECK(cost > 0)         NOT NULL);

    #   CREATE TABLE PhotoInDisk   (disk_ID        INTEGER     REFERENCES DiskTable,
    #                               photo_ID       INTEGER     REFERENCES PhotoTable,  UNIQUE(disk_ID, photo_ID));

    #   CREATE TABLE RAMInDisk     (disk_ID        INTEGER     REFERENCES DiskTable,
    #                               ram_ID         INTEGER     REFERENCES RAMTable,    UNIQUE(disk_ID, ram_ID));

    #
    pass


def clearTables():
    pass


def dropTables():
    pass


def addPhoto(photo: Photo) -> ReturnValue:

    #   INSERT INTO PhotoTable
    #        VALUES (id, description, size);

    return ReturnValue.OK


def getPhotoByID(photoID: int) -> Photo:

    #

    return Photo()


def deletePhoto(photo: Photo) -> ReturnValue:
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
    return ReturnValue.OK


def addPhotoToDisk(photo: Photo, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def removePhotoFromDisk(photo: Photo, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def addRAMToDisk(ramID: int, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def removeRAMFromDisk(ramID: int, diskID: int) -> ReturnValue:
    return ReturnValue.OK


def averagePhotosSizeOnDisk(diskID: int) -> float:
    return 0


def getTotalRamOnDisk(diskID: int) -> int:
    return 0


def getCostForDescription(description: str) -> int:
    return 0


def getPhotosCanBeAddedToDisk(diskID: int) -> List[int]:
    return []


def getPhotosCanBeAddedToDiskAndRAM(diskID: int) -> List[int]:
    return []


def isCompanyExclusive(diskID: int) -> bool:
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
