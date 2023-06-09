from typing import List
import Utility.DBConnector as Connector
from Utility.DBConnector import ResultSet
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


    # @@@@@@@@@@@@@@ VIEWs @@@@@@@@@@@@@@

    PhotoDataVIEW = "CREATE VIEW PhotoDataVIEW AS                                       \
                        SELECT disk_ID,                                                 \
                               PhotoInDisk.photo_ID AS photo_ID,                        \
                               description, size                                        \
                          FROM PhotoInDisk LEFT OUTER JOIN PhotoTable                   \
                            ON PhotoInDisk.photo_ID = PhotoTable.photo_ID; "

    RamDataVIEW = "CREATE VIEW RamDataVIEW AS                                           \
                        SELECT disk_ID,                                                 \
                               RamInDisk.ram_ID AS ram_ID,                              \
                               company, size                                            \
                          FROM RamInDisk LEFT OUTER JOIN RamTable                       \
                            ON RamInDisk.ram_ID = RamTable.ram_ID; "


    # for getPhotosCanBeAdded:
    PhotoBySizeVIEW = "CREATE VIEW PhotoBySizeVIEW AS                                   \
                                SELECT photo_ID, size                                   \
                                  FROM PhotoTable; "
    
    DiskBySpaceAndRamVIEW = "CREATE VIEW DiskBySpaceAndRamVIEW AS                       \
                                SELECT disk_ID,                                         \
                                       free_space,                                      \
                                       (SELECT SUM(size)                                \
                                          FROM RamDataVIEW                              \
                                         WHERE disk_ID = DT.disk_ID) AS sum_ram         \
                                  FROM DiskTable DT; "

    PhotosCanBeAddedVIEW = "CREATE VIEW PhotosCanBeAddedVIEW AS                         \
                                SELECT disk_ID,                                         \
                                       photo_ID                                         \
                                  FROM DiskBySpaceAndRamVIEW,                           \
                                       PhotoBySizeVIEW                                  \
                                 WHERE free_space >= size; "
     
    CanBeAddedToDiskAndRamVIEW = "CREATE VIEW CanBeAddedToDiskAndRamVIEW AS             \
                                SELECT disk_ID,                                         \
                                       photo_ID                                         \
                                  FROM DiskBySpaceAndRamVIEW,                           \
                                       PhotoBySizeVIEW                                  \
                                 WHERE size = 0 OR (sum_ram IS NOT NULL                 \
                                                    AND sum_ram >= size                 \
                                                    AND free_space >= size); "


    # for isDiskContainingAtLeastNumExists:
    DescriptionsInDiskVIEW = "CREATE VIEW DescriptionsInDiskVIEW AS                     \
                                SELECT disk_ID,                                         \
                                       description,                                     \
                                       COUNT(description) AS num                        \
                                  FROM PhotoDataVIEW                                    \
                                 GROUP BY disk_ID, description; "


    # for getClosePhotos:
    PhotoNotInDiskVIEW = "CREATE VIEW PhotoNotInDiskVIEW AS                             \
                                SELECT D.disk_ID  AS disk_ID,                           \
                                       P.photo_ID AS photo_ID                           \
                                  FROM (SELECT disk_ID FROM DiskTable)   AS D,          \
                                       (SELECT photo_ID FROM PhotoTable) AS P           \
                                 WHERE P.photo_ID NOT IN (SELECT photo_ID               \
                                                            FROM PhotoInDisk            \
                                                           WHERE disk_ID = D.disk_ID); "

    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(PhotoTable + RamTable + DiskTable + 
                     PhotoInDisk + RamInDisk +
                     PhotoDataVIEW + RamDataVIEW +
                     PhotoBySizeVIEW + DiskBySpaceAndRamVIEW + 
                     PhotosCanBeAddedVIEW + CanBeAddedToDiskAndRamVIEW +
                     DescriptionsInDiskVIEW + PhotoNotInDiskVIEW)
        conn.commit()
    except Exception as e:
        print("createTables exception: " + str(e))
    conn.close()


def clearTables():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DELETE FROM RamInDisk;    \
                      DELETE FROM PhotoInDisk;  \
                      DELETE FROM DiskTable;    \
                      DELETE FROM RamTable;     \
                      DELETE FROM PhotoTable")
        conn.commit()
    except Exception as e:
        # print(e)
        pass
    conn.close()


def dropTables():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DROP TABLE IF EXISTS RamInDisk    CASCADE;    \
                      DROP TABLE IF EXISTS PhotoInDisk  CASCADE;    \
                      DROP TABLE IF EXISTS DiskTable    CASCADE;    \
                      DROP TABLE IF EXISTS RamTable     CASCADE;    \
                      DROP TABLE IF EXISTS PhotoTable   CASCADE")
        conn.commit()
    except Exception as e:
        # print(e)
        pass
    conn.close()


def addPhoto(photo: Photo) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO PhotoTable    \
                 VALUES ({id}, {description}, {size})"
            ).format(
                id = sql.Literal(photo.getPhotoID()),
                description = sql.Literal(photo.getDescription()),
                size = sql.Literal(photo.getSize())
            )
        )
        conn.commit()
    except (DatabaseException.NOT_NULL_VIOLATION, 
            DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except Exception as e:
        # print(e)
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def getPhotoByID(photoID: int) -> Photo:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT *               \
                   FROM PhotoTable      \
                  WHERE photo_ID = {photo_id}"
            ).format(photo_id = sql.Literal(photoID))
        )
        conn.commit()
    except Exception:
        pass
    conn.close()

    ret_val = Photo.badPhoto()
    if not result.isEmpty():
        ret_val.setPhotoID(result[0]['photo_ID'])
        ret_val.setDescription(result[0]['description'])
        ret_val.setSize(result[0]['size'])
    return ret_val


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
                DELETE FROM PhotoInDisk                             \
                 WHERE photo_ID = {photo_id};                       \
                                                                    \
                DELETE FROM PhotoTable                              \
                 WHERE photo_ID = {photo_id}"
            ).format(
                size = sql.Literal(photo.getSize()), 
                photo_id = sql.Literal(photo.getPhotoID())
            )
        )
        conn.commit()
    except Exception as e:
        # print(e)
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def addDisk(disk: Disk) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO DiskTable  \
                 VALUES ({id}, {company}, {speed}, {free_space}, {cost})"
            ).format(
                id =            sql.Literal(disk.getDiskID()),
                company =       sql.Literal(disk.getCompany()),
                speed =         sql.Literal(disk.getSpeed()),
                free_space =    sql.Literal(disk.getFreeSpace()),
                cost =          sql.Literal(disk.getCost())
            )
        )
        conn.commit()
    except (DatabaseException.NOT_NULL_VIOLATION, 
            DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def getDiskByID(diskID: int) -> Disk:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT *               \
                   FROM DiskTable       \
                  WHERE disk_ID = {}"
            ).format(sql.Literal(diskID))
        )
        conn.commit()
    except Exception:
        pass
    conn.close()

    ret_val = Disk.badDisk()
    if not result.isEmpty():
        ret_val.setDiskID(result[0]['disk_ID'])
        ret_val.setCompany(result[0]['company'])
        ret_val.setSpeed(result[0]['speed'])
        ret_val.setFreeSpace(result[0]['free_space'])
        ret_val.setCost(result[0]['cost']) 
    return ret_val


def deleteDisk(diskID: int) -> ReturnValue:
    conn = None
    rows_effected, _ = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM PhotoInDisk        \
                  WHERE disk_ID = {disk_id};    \
                                                \
                DELETE FROM RamInDisk           \
                 WHERE disk_ID = {disk_id};     \
                                                \
                DELETE FROM DiskTable           \
                 WHERE disk_ID = {disk_id}"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception as e:
        # print(e)
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK if rows_effected > 0 else ReturnValue.NOT_EXISTS


def addRAM(ram: RAM) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO RamTable   \
                 VALUES ({id}, {company}, {size})"
            ).format(
                id = sql.Literal(ram.getRamID()),
                company = sql.Literal(ram.getCompany()),
                size = sql.Literal(ram.getSize())
            )  
        )
        conn.commit()
    except (DatabaseException.NOT_NULL_VIOLATION, 
            DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def getRAMByID(ramID: int) -> RAM:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT *               \
                   FROM RamTable        \
                  WHERE ram_ID = {}"
            ).format(sql.Literal(ramID))
        )
        conn.commit()
    except Exception:
        pass
    conn.close()

    ret_val = RAM.badRAM()
    if not result.isEmpty():
        ret_val.setRamID(result[0]['ram_ID']) 
        ret_val.setCompany(result[0]['company'])
        ret_val.setSize(result[0]['size'])
    return ret_val


def deleteRAM(ramID: int) -> ReturnValue:
    conn = None
    rows_effected, _ = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM RamInDisk                              \
                 WHERE ram_ID = {ram_id};                           \
                                                                    \
                DELETE FROM RamTable                                \
                 WHERE ram_ID = {ram_id}"
            ).format(
                ram_id = sql.Literal(ramID)
            )
        )
        conn.commit()
    except Exception as e:
        # print(e)
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
                      VALUES ({disk_id}, {company}, {speed}, {free_space}, {cost})"
            ).format(
                photo_id =      sql.Literal(photo.getPhotoID()),
                description =   sql.Literal(photo.getDescription()),
                size =          sql.Literal(photo.getSize()), 
                disk_id =       sql.Literal(disk.getDiskID()),
                company =       sql.Literal(disk.getCompany()),
                speed =         sql.Literal(disk.getSpeed()),
                free_space =    sql.Literal(disk.getFreeSpace()),
                cost =          sql.Literal(disk.getCost())
            )
        )
    except DatabaseException.UNIQUE_VIOLATION:
        conn.rollback()
        return ReturnValue.ALREADY_EXISTS
    except Exception:
        conn.rollback()
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
                "INSERT INTO PhotoInDisk                        \
                 VALUES ({disk_id}, {photo_id});                \
                                                                \
                UPDATE DiskTable                                \
                   SET free_space = free_space - {photo_size}   \
                 WHERE disk_ID = {disk_id}"
            ).format(
                disk_id = sql.Literal(diskID),
                photo_id = sql.Literal(photo.getPhotoID()),
                photo_size = sql.Literal(photo.getSize())
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
        conn.rollback()
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
                   AND photo_ID = {photo_id}"
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
                 VALUES ({disk_id}, {ram_id})"
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
    rows_effected, _ = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(
            sql.SQL(
                "DELETE FROM RamInDisk          \
                  WHERE disk_ID = {disk_id}     \
                    AND ram_ID = {ram_id}"
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
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT AVG(size) AS avg        \
                   FROM PhotoDataVIEW           \
                  WHERE disk_ID = {disk_id}"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception as e:
        print("averagePhotosSizeOnDisk exception: " + str(e))
        return -1
    finally:
        conn.close()
    
    if result.isEmpty() or result[0]['avg'] is None:
        return 0
    
    return result[0]['avg']


def getTotalRamOnDisk(diskID: int) -> int:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT SUM(size) AS sum        \
                   FROM RamDataVIEW             \
                  WHERE disk_ID = {disk_id}"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception:
        return -1
    finally:
        conn.close()
    return 0 if result[0]['sum'] is None else result[0]['sum']


def getCostForDescription(description: str) -> int:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT SUM(PD.size * DT.cost) AS sum       \
                   FROM PhotoDataVIEW PD,                   \
                        DiskTable DT                        \
                  WHERE PD.disk_ID = DT.disk_ID             \
                    AND PD.description = {description}"
            ).format(
                description = sql.Literal(description)
            )
        )
        conn.commit()
    except Exception as e:
        print("getCostForDescription exception: " + str(e))
        return -1
    finally:
        conn.close()

    if result.isEmpty() or result[0]['sum'] is None:
        return 0

    return result[0]['sum']


def getPhotosCanBeAddedToDisk(diskID: int) -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT photo_ID                \
                   FROM PhotosCanBeAddedVIEW    \
                  WHERE disk_ID = {disk_id}     \
                  ORDER BY photo_ID DESC        \
                  LIMIT 5"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()
    return getIDsAUX(result, 'photo_ID')


def getPhotosCanBeAddedToDiskAndRAM(diskID: int) -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT photo_ID                        \
                   FROM CanBeAddedToDiskAndRamVIEW      \
                  WHERE disk_ID = {disk_id}             \
                  ORDER BY photo_ID ASC                 \
                  LIMIT 5"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception as e:
        # print(e)
        pass
    finally:
        conn.close()

    return getIDsAUX(result, 'photo_ID')


def isCompanyExclusive(diskID: int) -> bool:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT company FROM DiskTable WHERE disk_ID = {disk_id}        \
                    UNION                                                       \
                SELECT company FROM RamDataVIEW WHERE disk_ID = {disk_id}"
            ).format(
                disk_id = sql.Literal(diskID)
            )
        )
        conn.commit()
    except Exception:
        pass
    conn.close()
    return result.size() == 1


def isDiskContainingAtLeastNumExists(description: str, num: int) -> bool:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT disk_ID                         \
                   FROM DescriptionsInDiskVIEW          \
                  WHERE description = {description}     \
                    AND num >= {num}"
            ).format(
                description = sql.Literal(description),
                num = sql.Literal(num)
            )
        )
        conn.commit()
    except Exception as e:
        print("isDiskContainingAtLeastNumExists exception: " + str(e))
    conn.close()
    return result.isEmpty() == False


def getDisksContainingTheMostData() -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            "SELECT disk_ID, SUM(size)                          \
               FROM ((SELECT disk_ID, COUNT(*) AS size          \
                        FROM DiskTable GROUP BY disk_ID)        \
                    UNION ALL                                   \
                     (SELECT disk_ID, size FROM PhotoDataVIEW)  \
                    ) AS DS                                     \
              GROUP BY disk_ID                                  \
              ORDER BY SUM(size) DESC, disk_ID ASC              \
              LIMIT 5"
        )
        conn.commit()
    except Exception as e:
        print("getDisksContainingTheMostData exception: " + str(e))
    conn.close()
    return getIDsAUX(result, 'disk_ID')


### Advanced API ###

def getConflictingDisks() -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            "SELECT DISTINCT disk_ID                                \
               FROM PhotoDataVIEW PD                                \
              WHERE photo_ID IN (SELECT photo_ID                    \
                                   FROM PhotoDataVIEW               \
                                  WHERE disk_ID <> PD.disk_ID)      \
              ORDER BY disk_ID ASC"
        )
        conn.commit()
    except Exception:
        pass
    conn.close()
    return getIDsAUX(result, 'disk_ID')


def mostAvailableDisks() -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            "SELECT disk_ID,                                        \
                    speed,                                          \
                    (SELECT COUNT(photo_ID)                         \
                       FROM PhotosCanBeAddedVIEW                    \
                      WHERE disk_ID = DT.disk_ID) AS num_photos     \
               FROM DiskTable DT                                    \
              ORDER BY num_photos DESC,                             \
                       speed      DESC,                             \
                       disk_ID    ASC                               \
              LIMIT 5"
        )
        conn.commit()
    except Exception:
        pass
    conn.close()
    return getIDsAUX(result, 'disk_ID')


def getClosePhotos(photoID: int) -> List[int]:
    conn = None
    _, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(
            sql.SQL(
                "SELECT photo_ID                                                            \
                   FROM PhotoTable                                                          \
                  WHERE photo_ID                                                            \
                    NOT IN (SELECT photo_ID                                                 \
                              FROM PhotoNotInDiskVIEW                                       \
                             WHERE disk_ID IN (SELECT disk_ID                               \
                                                 FROM PhotoInDisk                           \
                                                WHERE photo_ID = {photo_id})                \
                             GROUP BY photo_ID                                              \
                            HAVING COUNT(disk_ID) > (SELECT COUNT(disk_ID)                  \
                                                       FROM PhotoInDisk                     \
                                                      WHERE photo_ID = {photo_id})/2 )      \
                    AND photo_ID <> {photo_id}                                              \
                  ORDER BY photo_ID ASC                                                     \
                  LIMIT 10"
            ).format(
                photo_id = sql.Literal(photoID)
            )
        )
        conn.commit()
    except Exception:
        pass
    conn.close()  
    return getIDsAUX(result, 'photo_ID')


def getIDsAUX(result: ResultSet, lable: str) -> List[int]:
    ret_val = []
    for i in range(result.size()):
        ret_val.append(result[i][lable])
    return ret_val

