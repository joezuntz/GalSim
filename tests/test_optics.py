import galsim.optics
import numpy as np

testshape = (512, 512)  # shape of image arrays for all tests

decimal = 10     # Last decimal place used for checking equality of float arrays, see
                 # np.testing.assert_array_almost_equal()

decimal_dft = 3  # Last decimal place used for checking near equality of DFT product matrices to
                 # continuous-result derived check values... note this is not as stringent as
                 # decimal, because this is tough, because the DFT representation of a function is
                 # not precisely equivalent to its continuous counterpart.
                 # See http://en.wikipedia.org/wiki/File:From_Continuous_To_Discrete_Fourier_Transform.gif

def test_roll2d_circularity():
    """Test both integer and float arrays are unchanged by full circular roll.
    """
    # Make heterogenous 2D array, integers first, test that a full roll gives the same as the inputs
    int_image = np.random.random_integers(low=0, high=1, size=testshape)
    np.testing.assert_array_equal(int_image,
                                  galsim.optics.roll2d(int_image, int_image.shape),
                                  err_msg='galsim.optics.roll2D failed int array circularity test')
    # Make heterogenous 2D array, this time floats
    flt_image = np.random.random(size=testshape)
    np.testing.assert_array_equal(flt_image,
                                  galsim.optics.roll2d(flt_image, flt_image.shape),
                                  err_msg='galsim.optics.roll2D failed flt array circularity test')

def test_roll2d_fwdbck():
    """Test both integer and float arrays are unchanged by unit forward and backward roll.
    """
    # Make heterogenous 2D array, integers first, test that a +1, -1 roll gives the same as initial
    int_image = np.random.random_integers(low=0, high=1, size=testshape)
    np.testing.assert_array_equal(int_image,
                                  galsim.optics.roll2d(galsim.optics.roll2d(int_image, (+1, +1)),
                                                       (-1, -1)),
                                  err_msg='galsim.optics.roll2D failed int array fwd/back test')
    # Make heterogenous 2D array, this time floats
    flt_image = np.random.random(size=testshape)
    np.testing.assert_array_equal(flt_image,
                                  galsim.optics.roll2d(galsim.optics.roll2d(flt_image, (+1, +1)),
                                                       (-1, -1)),
                                  err_msg='galsim.optics.roll2D failed flt array fwd/back test')

def test_roll2d_join():
    """Test both integer and float arrays are equivalent if rolling +1/-1 or -/+(shape[i/j] - 1).
    """
    # Make heterogenous 2D array, integers first
    int_image = np.random.random_integers(low=0, high=1, size=testshape)
    np.testing.assert_array_equal(galsim.optics.roll2d(int_image, (+1, -1)),
                                  galsim.optics.roll2d(int_image, (-(int_image.shape[0] - 1),
                                                                   +(int_image.shape[1] - 1))),
                                  err_msg='galsim.optics.roll2D failed int array +/- join test')
    np.testing.assert_array_equal(galsim.optics.roll2d(int_image, (-1, +1)),
                                  galsim.optics.roll2d(int_image, (+(int_image.shape[0] - 1),
                                                                   -(int_image.shape[1] - 1))),
                                  err_msg='galsim.optics.roll2D failed int array -/+ join test')
    # Make heterogenous 2D array, this time floats
    flt_image = np.random.random(size=testshape)
    np.testing.assert_array_equal(galsim.optics.roll2d(flt_image, (+1, -1)),
                                  galsim.optics.roll2d(flt_image, (-(flt_image.shape[0] - 1),
                                                                   +(flt_image.shape[1] - 1))),
                                  err_msg='galsim.optics.roll2D failed flt array +/- join test')
    np.testing.assert_array_equal(galsim.optics.roll2d(flt_image, (-1, +1)),
                                  galsim.optics.roll2d(flt_image, (+(flt_image.shape[0] - 1),
                                                                   -(flt_image.shape[1] - 1))),
                                  err_msg='galsim.optics.roll2D failed flt array -/+ join test')

def test_kxky():
    """Test that the basic properties of kx and ky are right.
    """
    kx, ky = galsim.optics.kxky((4, 4))
    kxref = np.array([0., 0.25, -0.5, -0.25]) * 2. * np.pi
    kyref = np.array([0., 0.25, -0.5, -0.25]) * 2. * np.pi
    for i in xrange(4):
        np.testing.assert_array_almost_equal(kx[i, :], kxref, decimal=decimal,
                                             err_msg='failed kx equivalence on row i = '+str(i))
    for j in xrange(4):
        np.testing.assert_array_almost_equal(ky[:, j], kyref, decimal=decimal,
                                             err_msg='failed ky equivalence on row j = '+str(j))

def test_kxky_plusone():
    """Test that the basic properties of kx and ky are right...
    But increment testshape used in test_kxky by one to test both odd and even cases.
    """
    kx, ky = galsim.optics.kxky((4 + 1, 4 + 1))
    kxref = np.array([0., 0.2, 0.4, -0.4, -0.2]) * 2. * np.pi
    kyref = np.array([0., 0.2, 0.4, -0.4, -0.2]) * 2. * np.pi
    for i in xrange(4 + 1):
        np.testing.assert_array_almost_equal(kx[i, :], kxref, decimal=decimal,
                                             err_msg='failed kx equivalence on row i = '+str(i))
    for j in xrange(4 + 1):
        np.testing.assert_array_almost_equal(ky[:, j], kyref, decimal=decimal,
                                             err_msg='failed ky equivalence on row j = '+str(j))

def test_check_all_contiguous():
    """Test all galsim.optics outputs are C-contiguous as required by the galsim.Image class.
    """
    #Check that roll2d outputs contiguous arrays whatever the input
    imcstyle = np.random.random(size=testshape)
    rolltest = galsim.optics.roll2d(imcstyle, (+1, -1))
    assert rolltest.flags.c_contiguous
    imfstyle = np.random.random(size=testshape).T
    rolltest = galsim.optics.roll2d(imfstyle, (+1, -1))
    assert rolltest.flags.c_contiguous
    # Check kx, ky
    kx, ky = galsim.optics.kxky(testshape)
    assert kx.flags.c_contiguous
    assert ky.flags.c_contiguous
    # Check basic outputs from wavefront, psf and mtf (array contents won't matter, so we'll use
    # a pure circular pupil)
    assert galsim.optics.wavefront(array_shape=testshape).flags.c_contiguous
    assert galsim.optics.psf(array_shape=testshape).flags.c_contiguous
    assert galsim.optics.otf(array_shape=testshape).flags.c_contiguous
    assert galsim.optics.mtf(array_shape=testshape).flags.c_contiguous
    assert galsim.optics.ptf(array_shape=testshape).flags.c_contiguous

def test_simple_wavefront():
    """Test the MTF of a pure circular pupil against the known result.
    """
    kx, ky = galsim.optics.kxky(testshape)
    kmax_test = 0.75 * np.pi # Choose some kmax for the test
    kmag = np.sqrt(kx**2 + ky**2) / kmax_test # Set up array of |k| in units of kmax_test
    # Simple pupil wavefront should merely be unit ordinate tophat of radius kmax / 2: 
    in_pupil = kmag < .5
    wf_true = np.zeros(kmag.shape)
    wf_true[in_pupil] = 1.
    # Compare
    wf = galsim.optics.wavefront(array_shape=testshape, kmax=kmax_test)
    np.testing.assert_array_almost_equal(wf, wf_true, decimal=decimal)

def test_simple_mtf():
    """Test the MTF of a pure circular pupil against the known result.
    """
    kx, ky = galsim.optics.kxky(testshape)
    kmax_test = 0.75 * np.pi # Choose some kmax for the test
    kmag = np.sqrt(kx**2 + ky**2) / kmax_test # Set up array of |k| in units of kmax_test
    in_pupil = kmag < 1.
    # Then use analytic formula for MTF of circ pupil (fun to derive)
    mtf_true = np.zeros(kmag.shape)
    mtf_true[in_pupil] = (np.arccos(kmag[in_pupil]) - kmag[in_pupil] *
                          np.sqrt(1. - kmag[in_pupil]**2)) * 2. / np.pi
    # Compare
    mtf = galsim.optics.mtf(array_shape=testshape, kmax=kmax_test)
    np.testing.assert_array_almost_equal(mtf, mtf_true, decimal=decimal_dft)

def test_simple_ptf():
    """Test the PTF of a pure circular pupil against the known result (zero).
    """
    ptf_true = np.zeros(testshape)
    # Compare
    ptf = galsim.optics.ptf(array_shape=testshape)
    # Test via median absolute deviation, since occasionally things around the edge of the OTF get
    # hairy when dividing a small number by another small number
    nmad_ptfdiff = np.median(np.abs(ptf - np.median(ptf_true)))
    assert nmad_ptfdiff <= 10.**(-decimal)

def test_consistency_psf_mtf():
    """Test that the MTF of a pure circular pupil is |FT{PSF}|.
    """
    kx, ky = galsim.optics.kxky(testshape)
    kmax_test = 0.75 * np.pi # Choose some kmax for the test
    psf = galsim.optics.psf(array_shape=testshape, kmax=kmax_test)
    mtf_test = np.abs(np.fft.fft2(psf))
    # Compare
    mtf = galsim.optics.mtf(array_shape=testshape, kmax=kmax_test)
    np.testing.assert_array_almost_equal(mtf, mtf_test, decimal=decimal_dft)
