import unittest
import Solution
from Utility.ReturnValue import ReturnValue
from Tests.abstractTest import AbstractTest
from Business.Photo import Photo
from Business.RAM import RAM
from Business.Disk import Disk

photo1 = Photo(1, "dog", 12)
photo2 = Photo(2, "cat", 8)
photo3 = Photo(3, "house", 30)
photo4 = Photo(4, "dog", 12)
photo5 = Photo(5, "dog", 12)
photo6 = Photo(6, "ball", 5)

ram1 = RAM(1, "sanDisk", 45)
ram2 = RAM(2, "samsung", 45)
ram3 = RAM(3, "samsung", 60)
ram4 = RAM(4, "sanDisk", 60)
ram5 = RAM(5, "sanDisk", 90)

disk1 = Disk(1, "sanDisk", 20, 100, 7)
disk2 = Disk(2, "samsung", 26, 200, 9)
disk3 = Disk(3, "samsung", 20, 30, 40)


class myTest1(AbstractTest):

    ################# addX #################

    def test_addPhoto(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(photo1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(photo2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(photo3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(photo4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(photo5), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhoto(Photo(None, "dog", 12)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhoto(Photo(1, None, 12)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhoto(Photo(1, "dog", None)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhoto(Photo(0, "dog", 12)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhoto(Photo(1, "dog", -1)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPhoto(photo1), "UNIQUE_VIOLATION")

    def tets_addRAM(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addRAM(ram1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAM(ram2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAM(ram3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAM(ram4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAM(ram5), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addRAM(RAM(None, "dog", 12)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addRAM(RAM(1, None, 12)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addRAM(RAM(1, "dog", None)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addRAM(RAM(0, "dog", 12)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addRAM(RAM(1, "dog", -1)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addRAM(RAM(1, "dog", 12)), "UNIQUE_VIOLATION")

    def test_addDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addDisk(disk1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(disk2), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(None, "sanDisk", 20, 10, 7)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(1, None, 20, 10, 7)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(1, "sanDisk", None, 10, 7)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(1, "sanDisk", 20, None, 7)), "NOT_NULL_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(1, "sanDisk", 20, 10, )), "NOT_NULL_VIOLATION")
        # test CHECK_VIOLATION:
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(-1, "sanDisk", 20, 10, 7)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(3, "sanDisk", -1, 10, 7)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(1, "sanDisk", 20, -1, 7)), "CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addDisk(Disk(3, "sanDisk", 20, 10, -1)), "CHECK_VIOLATION")
        # test UNIQUE_VIOLATION:
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addDisk(Disk(1, "sanDisk", 20, 10, 7)), "UNIQUE_VIOLATION")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addDisk(Disk(2, "sanDisk", 20, 10, 7)), "UNIQUE_VIOLATION")

    def test_addDiskAndPhoto(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addDiskAndPhoto(disk3, photo6), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addDiskAndPhoto(Disk(1, "sanDisk", 20, 10, 7), Photo(7, "ball", 5)),
                          "disk already exists")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addDiskAndPhoto(Disk(7, "samsung", 20, 30, 40), photo1), 
                         "photo already exists")
        # delete the changes in this function:
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo6), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteDisk(disk3), "Should work")


    ################# getXByID #################

    def test_getPhotoByID(self) -> None:
        self.assertEqual(photo1, Solution.getPhotoByID(1), "Should work")
        self.assertEqual(photo2, Solution.getPhotoByID(2), "Should work")
        self.assertEqual(photo3, Solution.getPhotoByID(3), "Should work")
        self.assertEqual(photo4, Solution.getPhotoByID(4), "Should work")
        self.assertEqual(photo5, Solution.getPhotoByID(5), "Should work")
        # tets Exceptions:
        self.assertEqual(Photo.badPhoto(), Solution.getPhotoByID(6), "photo_ID not exists")

    def test_getRAMByID(self) -> None:
        self.assertEqual(ram1, Solution.getRAMByID(1), "Should work")
        self.assertEqual(ram2, Solution.getRAMByID(2), "Should work")
        self.assertEqual(ram3, Solution.getRAMByID(3), "Should work")
        self.assertEqual(ram4, Solution.getRAMByID(4), "Should work")
        self.assertEqual(ram5, Solution.getRAMByID(5), "Should work")
        # tets Exceptions:
        self.assertEqual(RAM.badRAM(), Solution.getRAMByID(6), "ram_ID not exists")

    def test_getDiskByID(self) -> None:
        self.assertEqual(Disk(1, "sanDisk", 20, 10, 7), Solution.getDiskByID(1), "Should work")
        self.assertEqual(Disk(2, "samsung", 26, 15, 9), Solution.getDiskByID(2), "Should work")
        # tets Exceptions:
        self.assertEqual(Disk.badDisk(), Solution.getDiskByID(3), "disk_ID not exists")

    ################# addXToDisk #################

    def test_addPhotoToDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(photo2, 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(photo3, 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(photo3, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(photo4, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(photo5, 2), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.addPhotoToDisk(photo6, 2), "photo not exists, FOREIGN_KEY_VIOLATION")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.addPhotoToDisk(photo1, 3), "disk not exists, FOREIGN_KEY_VIOLATION")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPhotoToDisk(photo2, 1), "photo2 already in disk1, UNIQUE_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhotoToDisk(Photo(7, "large photo", 800), 1), 
                         "there is not enough free_space on the disk, CHECK_VIOLATION")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPhotoToDisk(Photo(7, "large photo", 80), 1), 
                         "there is not enough free_space on the disk, CHECK_VIOLATION")
        
    def test_addRAMToDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addRAMToDisk(4, 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAMToDisk(1, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addRAMToDisk(3, 2), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.addRAMToDisk(6, 1), "ram not exists, FOREIGN_KEY_VIOLATION")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.addRAMToDisk(4, 3), "disk not exists, FOREIGN_KEY_VIOLATION")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addRAMToDisk(4, 1), "ram4 already in disk1, UNIQUE_VIOLATION")

    ################# removeXFromDisk #################

    def test_removePhotoFromDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo2, 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo4, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo5, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo6, 1), "Should work, although photo6 does not exist")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo2, 3), "Should work, although disk3 does not exist")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo5, 1), "Should work, although photo5 is not saved on disk1")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(photo1, 2), "Should work, although photo1 is not saved on disk2")

    def test_removeRAMFromDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.removeRAMFromDisk(4, 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.removeRAMFromDisk(1, 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.removeRAMFromDisk(3, 2), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.removeRAMFromDisk(6, 1), "ram not exists")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.removeRAMFromDisk(4, 3), "disk not exists")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.removeRAMFromDisk(5, 1), "ram5 is not saved on disk1")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.removeRAMFromDisk(4, 1), "ram4 is already removed from disk1")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.removeRAMFromDisk(3, 2), "ram3 is already removed from disk2")

    ################# deleteX #################

    def test_deletePhoto(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo5), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo6), "Should work, although photo6 does not exist")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(photo1), "Should work, although photo1 already deleted")

    def test_deleteRAM(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.deleteRAM(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteRAM(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteRAM(3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteRAM(4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteRAM(5), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.deleteRAM(6), "ram6 is not exists")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.deleteRAM(1), "ram1 is already deleted")

    def test_deleteDisk(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.deleteDisk(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.deleteDisk(2), "Should work")
        # tets Exceptions:
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.deleteDisk(3), "disk3 is not exists")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.deleteDisk(1), "disk1 is already deleted")

    def test_clearTables(self) -> None:
        Solution.clearTables()



if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
