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
    pass


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)

