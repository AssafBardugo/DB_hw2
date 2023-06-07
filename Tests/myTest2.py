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


class myTest2(AbstractTest):
    def test_isDiskContainingAtLeastNumExists(self):
        self.assertFalse(Solution.isDiskContainingAtLeastNumExists("stuff", 1), "No disk yet")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(Disk(1, "HP", 10, 10, 10)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(Disk(2, "HP", 10, 20, 10)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(Photo(1, "stuff", 3)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(Photo(2, "stuff", 5)), "Should work")
        self.assertFalse(Solution.isDiskContainingAtLeastNumExists("stuff", 1), "No photo in disk yet")
        self.assertFalse(Solution.isDiskContainingAtLeastNumExists("stuff", 1), "No photo in disk yet")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(1, "stuff", 3), 1), "Should work")
        self.assertTrue(Solution.isDiskContainingAtLeastNumExists("stuff", 1), "Photo with stuff is there")
        self.assertFalse(Solution.isDiskContainingAtLeastNumExists("stuff", 2), "Only one photo is there")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(2, "stuff", 5), 1), "Should work")
        self.assertTrue(Solution.isDiskContainingAtLeastNumExists("stuff", 2), "Photo with stuff is there")
        self.assertFalse(Solution.isDiskContainingAtLeastNumExists("other", 2), "Only one photo is there")


    def test_getDisksContainingTheMostData(self):
        self.assertListEqual([], Solution.getDisksContainingTheMostData(), "No disks yet")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(Disk(2, "HP", 10, 20, 10)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(Disk(1, "HP", 10, 10, 10)), "Should work")
        self.assertListEqual([1, 2], Solution.getDisksContainingTheMostData(), "Should be 1,2 even no photos in")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(Photo(1, "stuff", 3)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhoto(Photo(2, "stuff", 5)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(1, "stuff", 3), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(2, "stuff", 5), 2), "Should work")
        self.assertListEqual([2, 1], Solution.getDisksContainingTheMostData(), "size of 2 is 5, size of 1 is 3")
        self.assertEqual(ReturnValue.OK, Solution.addDisk(Disk(3, "HP", 10, 20, 10)), "Should work")
        self.assertListEqual([2, 1, 3], Solution.getDisksContainingTheMostData(), "size of 2 is 5, size of 1 is 3, 3 is 0")
        self.assertEqual(ReturnValue.OK, Solution.removePhotoFromDisk(Photo(1, "stuff", 3), 1), "Should work")
        self.assertListEqual([2, 1, 3], Solution.getDisksContainingTheMostData(), "size of 2 is 5, size of 1 is 0, 3 is 0")
        self.assertEqual(ReturnValue.OK, Solution.deletePhoto(Photo(2, "stuff", 5)), "Should work")
        self.assertListEqual([1, 2, 3], Solution.getDisksContainingTheMostData(), "size of 2 is 0, size of 1 is 0, 3 is 0")
        self.assertEqual(ReturnValue.OK, Solution.addDiskAndPhoto(Disk(4, "HP", 10, 10, 10), Photo(7, "stuff", 10)),
                         "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(7, "stuff", 10), 4), "Should work")
        self.assertListEqual([4, 1, 2, 3], Solution.getDisksContainingTheMostData(),
                             "size of 2 is 0, size of 1 is 0, 3 is 0")
        self.assertEqual(ReturnValue.OK, Solution.addPhotoToDisk(Photo(7, "stuff", 10), 3), "Should work")
        self.assertListEqual([3, 4, 1, 2], Solution.getDisksContainingTheMostData(),
                             "size of 2 is 0, size of 1 is 0, 3 is 0")
        self.assertEqual(ReturnValue.OK, Solution.deleteDisk(3), "Should work")
        self.assertListEqual([4, 1, 2], Solution.getDisksContainingTheMostData(), "size of 2 is 0, size of 1 is 0, 3 is 0")


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)

