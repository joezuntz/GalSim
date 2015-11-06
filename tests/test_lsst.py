from __future__ import with_statement
import unittest
import numpy as np
import os
import galsim
from galsim.lsst import LsstCamera, LsstWCS
from galsim.celestial import CelestialCoord


class LsstCameraTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # these are taken from the header of the
        # galsim_afwCameraGeom_data.txt file generated by
        # GalSim/devel/external/generate_galsim_lsst_camera_validation.py
        cls.raPointing = 112.064181578541
        cls.decPointing = -33.015167519966
        cls.rotation = 27.0

        cls.validation_msg = "The LSST Camera outputs are no longer consistent\n" \
                             + "with the LSST Stack.  Contact Scott Daniel at scottvalscott@gmail.com\n" \
                             + "to make sure you have the correct version\n" \
                             + "\nYou can also try re-creating the test validation data\n" \
                             + "using the script GalSim/devel/external/generate_galsim_lsst_camera_validation.py"

        pointing = CelestialCoord(cls.raPointing*galsim.degrees, cls.decPointing*galsim.degrees)
        cls.camera = LsstCamera(pointing, cls.rotation*galsim.degrees)

        path, filename = os.path.split(__file__)
        file_name = os.path.join(path, 'random_data', 'galsim_afwCameraGeom_data.txt')
        dtype = np.dtype([('ra', np.float), ('dec', np.float), ('chipName', str, 100),
                           ('xpix', np.float), ('ypix', np.float),
                           ('xpup', np.float), ('ypup', np.float)])

        cls.camera_data = np.genfromtxt(file_name, dtype=dtype, delimiter='; ')


    def test_pupil_coordinates(self):
        """
        Test the conversion between (RA, Dec) and pupil coordinates.
        Results are checked against the routine provided by PALPY.
        """

        def palpyPupilCoords(star, pointing):
            """
            This is just a copy of the PALPY method Ds2tp, which
            I am taking to be the ground truth for projection from
            a sphere onto the tangent plane

            inputs
            ------------
            star is a CelestialCoord corresponding to the point being projected

            pointing is a CelestialCoord corresponding to the pointing of the
            'telescope'

            outputs
            ------------
            The x and y coordinates in the focal plane (radians)
            """

            ra = star.ra/galsim.radians
            dec = star.dec/galsim.radians
            ra_pointing = pointing.ra/galsim.radians
            dec_pointing = pointing.dec/galsim.radians

            cdec = np.cos(dec)
            sdec = np.sin(dec)
            cdecz = np.cos(dec_pointing)
            sdecz = np.sin(dec_pointing)
            cradif = np.cos(ra - ra_pointing)
            sradif = np.sin(ra - ra_pointing)

            denom = sdec * sdecz + cdec * cdecz * cradif
            xx = cdec * sradif/denom
            yy = (sdec * cdecz - cdec * sdecz * cradif)/denom
            return xx*galsim.radians, yy*galsim.radians


        np.random.seed(42)
        n_pointings = 10
        ra_pointing_list = np.random.random_sample(n_pointings)*2.0*np.pi
        dec_pointing_list = 0.5*(np.random.random_sample(n_pointings)-0.5)*np.pi
        rotation_angle_list = np.random.random_sample(n_pointings)*2.0*np.pi

        for ra, dec, rotation in zip(ra_pointing_list, dec_pointing_list, rotation_angle_list):

            pointing = CelestialCoord(ra*galsim.radians, dec*galsim.radians)
            camera = LsstCamera(pointing, rotation*galsim.radians)

            dra_list = (np.random.random_sample(100)-0.5)*0.5
            ddec_list = (np.random.random_sample(100)-0.5)*0.5

            star_list = np.array([CelestialCoord((ra+dra)*galsim.radians, (dec+ddec)*galsim.radians)
                                 for dra, ddec in zip(dra_list, ddec_list)])

            xTest, yTest = camera.pupilCoordsFromPoint(star_list)
            xControl = []
            yControl = []
            for star in star_list:
                xx, yy = palpyPupilCoords(star, pointing)
                xx *= -1.0
                xControl.append(xx*np.cos(rotation) - yy*np.sin(rotation))
                yControl.append(yy*np.cos(rotation) + xx*np.sin(rotation))

            xControl = np.array(xControl)
            yControl = np.array(yControl)

            np.testing.assert_array_almost_equal((xTest/galsim.arcsec) - (xControl/galsim.arcsec), np.zeros(len(xControl)),  7)
            np.testing.assert_array_almost_equal((yTest/galsim.arcsec) - (yControl/galsim.arcsec), np.zeros(len(yControl)), 7)


    def test_pupil_coordinates_from_floats(self):
        """
        Test that the method which converts floats into pupil coordinates agrees with the method
        that converts CelestialCoords into pupil coordinates
        """

        raPointing = 113.0
        decPointing = -25.6
        rot = 82.1
        pointing = CelestialCoord(raPointing*galsim.degrees, decPointing*galsim.degrees)
        camera = LsstCamera(pointing, rot*galsim.degrees)

        arcsec_per_radian = 180.0*3600.0/np.pi
        np.random.seed(33)
        raList = (np.random.random_sample(100)-0.5)*20.0+raPointing
        decList = (np.random.random_sample(100)-0.5)*20.0+decPointing
        pointingList = []
        for rr, dd in zip(raList, decList):
            pointingList.append(CelestialCoord(rr*galsim.degrees, dd*galsim.degrees))

        control_x, control_y = camera.pupilCoordsFromPoint(pointingList)
        test_x, test_y = camera.pupilCoordsFromFloat(np.radians(raList), np.radians(decList))

        np.testing.assert_array_almost_equal((test_x - control_x/galsim.radians)*arcsec_per_radian,
                                             np.zeros(len(test_x)), 10)


        np.testing.assert_array_almost_equal((test_y - control_y/galsim.radians)*arcsec_per_radian,
                                             np.zeros(len(test_y)), 10)


    def test_ra_dec_from_pupil_coords(self):
        """
        Test that the method which converts from pupil coordinates back to RA, Dec works
        """

        np.random.seed(55)
        n_samples = 100
        raList = (np.random.random_sample(n_samples)-0.5)*1.0 + np.radians(self.raPointing)
        decList = (np.random.random_sample(n_samples)-0.5)*1.0 + np.radians(self.decPointing)

        x_pupil, y_pupil = self.camera.pupilCoordsFromFloat(raList, decList)

        ra_test, dec_test = self.camera.raDecFromPupilCoords(x_pupil, y_pupil)

        np.testing.assert_array_almost_equal(np.cos(raList), np.cos(ra_test), 10)
        np.testing.assert_array_almost_equal(np.sin(raList), np.sin(ra_test), 10)
        np.testing.assert_array_almost_equal(np.cos(decList), np.cos(dec_test), 10)
        np.testing.assert_array_almost_equal(np.sin(decList), np.sin(dec_test), 10)


    def test_get_chip_name(self):
        """
        Test the method which associates positions on the sky with names of chips
        """

        # test case of a mapping a single location
        for rr, dd, control_name in \
            zip(self.camera_data['ra'], self.camera_data['dec'], self.camera_data['chipName']):

            point = CelestialCoord(rr*galsim.degrees, dd*galsim.degrees)
            test_name = self.camera.chipNameFromPoint(point)

            try:
                if control_name != 'None':
                    self.assertEqual(test_name, control_name)
                else:
                    self.assertEqual(test_name, None)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)

        # test case of mapping a list of celestial coords
        point_list = []
        for rr, dd in zip(self.camera_data['ra'], self.camera_data['dec']):
            point_list.append(CelestialCoord(rr*galsim.degrees, dd*galsim.degrees))

        test_name_list = self.camera.chipNameFromPoint(point_list)
        for test_name, control_name in zip(test_name_list, self.camera_data['chipName']):
            try:
                if control_name != 'None':
                    self.assertEqual(test_name, control_name)
                else:
                    self.assertEqual(test_name, None)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)


    def test_get_chip_name_from_float(self):
        """
        Test the method which associates positions on the sky (in terms of floats) with names of chips
        """

        # test case of a mapping a single location
        for rr, dd, control_name in \
            zip(self.camera_data['ra'], self.camera_data['dec'], self.camera_data['chipName']):

            test_name = self.camera.chipNameFromFloat(np.radians(rr), np.radians(dd))

            try:
                if control_name != 'None':
                    self.assertEqual(test_name, control_name)
                else:
                    self.assertEqual(test_name, None)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)

        # test case of mapping a list of celestial coords
        test_name_list = self.camera.chipNameFromFloat(np.radians(self.camera_data['ra']), np.radians(self.camera_data['dec']))
        for test_name, control_name in zip(test_name_list, self.camera_data['chipName']):
            try:
                if control_name != 'None':
                    self.assertEqual(test_name, control_name)
                else:
                    self.assertEqual(test_name, None)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)


    def test_pixel_coords_from_point(self):
        """
        Test method that goes from CelestialCoord to pixel coordinates
        """

        # test one at a time
        for rr, dd, x_control, y_control, name_control in \
            zip(self.camera_data['ra'], self.camera_data['dec'],
                self.camera_data['xpix'], self.camera_data['ypix'], self.camera_data['chipName']):

            point = CelestialCoord(rr*galsim.degrees, dd*galsim.degrees)
            x_test, y_test, name_test = self.camera.pixelCoordsFromPoint(point)
            try:
                if not np.isnan(x_test):
                    self.assertAlmostEqual(x_test, x_control, 6)
                    self.assertAlmostEqual(y_test, y_control, 6)
                    self.assertEqual(name_test, name_control)
                else:
                    self.assertTrue(np.isnan(x_control))
                    self.assertTrue(np.isnan(y_control))
                    self.assertTrue(np.isnan(y_test))
                    self.assertIsNone(name_test)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)

        # test lists
        pointing_list = []
        for rr, dd in zip(self.camera_data['ra'], self.camera_data['dec']):
            pointing_list.append(CelestialCoord(rr*galsim.degrees, dd*galsim.degrees))

        x_test, y_test, name_test_0 = self.camera.pixelCoordsFromPoint(pointing_list)

        name_test = np.array([nn if nn is not None else 'None' for nn in name_test_0])

        try:
            np.testing.assert_array_almost_equal(x_test, self.camera_data['xpix'], 6)
            np.testing.assert_array_almost_equal(y_test, self.camera_data['ypix'], 6)
            np.testing.assert_array_equal(name_test, self.camera_data['chipName'])
        except AssertionError as aa:
            print 'triggering error: ',aa.args[0]
            raise AssertionError(self.validation_msg)


    def test_pixel_coords_from_float(self):
        """
        Test method that goes from floats of RA, Dec to pixel coordinates
        """

        # test one at a time
        for rr, dd, x_control, y_control, name_control in \
            zip(self.camera_data['ra'], self.camera_data['dec'],
                self.camera_data['xpix'], self.camera_data['ypix'], self.camera_data['chipName']):

            x_test, y_test, name_test = self.camera.pixelCoordsFromFloat(np.radians(rr), np.radians(dd))
            try:
                if not np.isnan(x_test):
                    self.assertAlmostEqual(x_test, x_control, 6)
                    self.assertAlmostEqual(y_test, y_control, 6)
                    self.assertEqual(name_test, name_control)
                else:
                    self.assertTrue(np.isnan(x_control))
                    self.assertTrue(np.isnan(y_control))
                    self.assertTrue(np.isnan(y_test))
                    self.assertIsNone(name_test)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)

        # test lists
        pointing_list = []
        for rr, dd in zip(self.camera_data['ra'], self.camera_data['dec']):
            pointing_list.append(CelestialCoord(rr*galsim.degrees, dd*galsim.degrees))

        x_test, y_test, name_test_0 = self.camera.pixelCoordsFromFloat(np.radians(self.camera_data['ra']), np.radians(self.camera_data['dec']))

        name_test = np.array([nn if nn is not None else 'None' for nn in name_test_0])

        try:
            np.testing.assert_array_almost_equal(x_test, self.camera_data['xpix'], 6)
            np.testing.assert_array_almost_equal(y_test, self.camera_data['ypix'], 6)
            np.testing.assert_array_equal(name_test, self.camera_data['chipName'])
        except AssertionError as aa:
            print 'triggering error: ',aa.args[0]
            raise AssertionError(self.validation_msg)


    def test_pupil_coords_from_pixel_coords(self):
        """
        Test the conversion from pixel coordinates back into pupil coordinates
        """

        np.random.seed(88)
        n_samples = 100
        raList = (np.random.random_sample(n_samples)-0.5)*np.radians(1.5) + np.radians(self.raPointing)
        decList = (np.random.random_sample(n_samples)-0.5)*np.radians(1.5) + np.radians(self.decPointing)

        x_pup_control, y_pup_control = self.camera.pupilCoordsFromFloat(raList, decList)

        camera_point_list = self.camera._get_afw_pupil_coord_list_from_float(raList, decList)

        chip_name_possibilities = ('R:0,1 S:1,1', 'R:0,3 S:0,2', 'R:4,2 S:2,2', 'R:3,4 S:0,2')

        chip_name_list = [chip_name_possibilities[ii] for ii in np.random.random_integers(0,3,n_samples)]
        x_pix_list, y_pix_list = self.camera._pixel_coord_from_point_and_name(camera_point_list, chip_name_list)

        x_pup_test, y_pup_test = self.camera.pupilCoordsFromPixelCoords(x_pix_list, y_pix_list, chip_name_list)

        np.testing.assert_array_almost_equal(x_pup_test, x_pup_control, 10)
        np.testing.assert_array_almost_equal(y_pup_test, y_pup_control, 10)

        # test that NaNs are returned if chip_name is None or 'None'
        chip_name_list = ['None'] * len(x_pix_list)
        x_pup_test, y_pup_test = self.camera.pupilCoordsFromPixelCoords(x_pix_list, y_pix_list, chip_name_list)
        for xp, yp in zip(x_pup_test, y_pup_test):
            self.assertTrue(np.isnan(xp))
            self.assertTrue(np.isnan(yp))

        chip_name_list = [None] * len(x_pix_list)
        x_pup_test, y_pup_test = self.camera.pupilCoordsFromPixelCoords(x_pix_list, y_pix_list, chip_name_list)
        for xp, yp in zip(x_pup_test, y_pup_test):
            self.assertTrue(np.isnan(xp))
            self.assertTrue(np.isnan(yp))


    def test_ra_dec_from_pixel_coordinates(self):
        """
        Test the method that converts from pixel coordinates back to RA, Dec
        """

        ra_test, dec_test = self.camera.raDecFromPixelCoords(self.camera_data['xpix'], self.camera_data['ypix'], self.camera_data['chipName'])

        for rt, dt, rc, dc, name in \
            zip(ra_test, dec_test, np.radians(self.camera_data['ra']), np.radians(self.camera_data['dec']), self.camera_data['chipName']):

            if name != 'None':
                self.assertAlmostEqual(np.cos(rt), np.cos(rc))
                self.assertAlmostEqual(np.sin(rt), np.sin(rc))
                self.assertAlmostEqual(np.cos(dt), np.cos(dc))
                self.assertAlmostEqual(np.sin(dt), np.sin(dc))
            else:
                self.assertTrue(np.isnan(rt))
                self.assertTrue(np.isnan(dt))


        np.random.seed(99)
        n_samples = 100
        raList = (np.random.random_sample(n_samples)-0.5)*np.radians(1.5) + np.radians(self.raPointing)
        decList = (np.random.random_sample(n_samples)-0.5)*np.radians(1.5) + np.radians(self.decPointing)

        x_pup_control, y_pup_control = self.camera.pupilCoordsFromFloat(raList, decList)

        camera_point_list = self.camera._get_afw_pupil_coord_list_from_float(raList, decList)

        chip_name_possibilities = ('R:0,1 S:1,1', 'R:0,3 S:0,2', 'R:4,2 S:2,2', 'R:3,4 S:0,2')

        chip_name_list = [chip_name_possibilities[ii] for ii in np.random.random_integers(0,3,n_samples)]
        x_pix_list, y_pix_list = self.camera._pixel_coord_from_point_and_name(camera_point_list, chip_name_list)

        ra_test, dec_test = self.camera.raDecFromPixelCoords(x_pix_list, y_pix_list, chip_name_list)
        np.testing.assert_array_almost_equal(np.cos(ra_test), np.cos(raList))
        np.testing.assert_array_almost_equal(np.sin(ra_test), np.sin(raList))
        np.testing.assert_array_almost_equal(np.cos(dec_test), np.cos(decList))
        np.testing.assert_array_almost_equal(np.sin(dec_test), np.sin(decList))


class LsstWcsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # these are taken from the header of the
        # galsim_afwCameraGeom_forced_data.txt file generated by
        # GalSim/devel/external/generate_galsim_lsst_camera_validation.py
        cls.raPointing = 112.064181578541
        cls.decPointing = -33.015167519966
        cls.rotation = 27.0
        cls.chip_name = 'R:0,1 S:1,2'

        cls.validation_msg = "The LSST WCS outputs are no longer consistent\n" \
                             + "with the LSST Stack.  Contact Scott Daniel at scottvalscott@gmail.com\n" \
                             + "to make sure you have the correct version\n" \
                             + "\nYou can also try re-creating the test validation data\n" \
                             + "using the script GalSim/devel/external/generate_galsim_lsst_camera_validation.py"

        pointing = CelestialCoord(cls.raPointing*galsim.degrees, cls.decPointing*galsim.degrees)
        cls.wcs = LsstWCS(pointing, cls.rotation*galsim.degrees, cls.chip_name)

        dtype = np.dtype([('ra', np.float), ('dec', np.float), ('xpix', np.float), ('ypix', np.float)])

        path, filename = os.path.split(__file__)
        file_name = os.path.join(path, 'random_data', 'galsim_afwCameraGeom_forced_data.txt')
        cls.wcs_data = np.genfromtxt(file_name, dtype=dtype, delimiter='; ')


    def test_constructor(self):
        """
        Just make sure that the constructor for LsstWCS runs, and that it throws an error when you specify
        a nonsense chip.
        """

        pointing = CelestialCoord(112.0*galsim.degrees, -39.0*galsim.degrees)
        rotation = 23.1*galsim.degrees

        wcs1 = LsstWCS(pointing, rotation, 'R:1,1 S:2,2')

        with self.assertRaises(RuntimeError) as context:
            wcs2 = LsstWCS(pointing, rotation, 'R:1,1 S:3,3')
        self.assertEqual(context.exception.args[0],
                         "R:1,1 S:3,3 is not a valid chip_name for an LsstWCS")


    def test_xy(self):
        """
        Test that the conversion from RA, Dec to pixel coordinates works
        """

        # test one-at-a-time use case
        for rr, dd, x_control, y_control in \
            zip(np.radians(self.wcs_data['ra']), np.radians(self.wcs_data['dec']), self.wcs_data['xpix'], self.wcs_data['ypix']):

            x_test, y_test = self.wcs._xy(rr, dd)
            try:
                self.assertAlmostEqual(x_test, x_control, 6)
                self.assertAlmostEqual(y_test, y_control, 6)
            except AssertionError as aa:
                print 'triggering error: ',aa.args[0]
                raise AssertionError(self.validation_msg)

        # test list use case
        x_test, y_test = self.wcs._xy(np.radians(self.wcs_data['ra']), np.radians(self.wcs_data['dec']))
        try:
            np.testing.assert_array_almost_equal(x_test, self.wcs_data['xpix'], 6)
            np.testing.assert_array_almost_equal(y_test, self.wcs_data['ypix'], 6)
        except AssertionError as aa:
            print 'triggering error: ',aa.args[0]
            raise AssertionError(self.validation_msg)
