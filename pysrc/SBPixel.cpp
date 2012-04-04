#include "boost/python.hpp"
#include "Interpolant.h"
#include "SBPixel.h"

namespace bp = boost::python;

namespace galsim {
namespace {

struct PySBPixel {

    static void wrap() {
        bp::class_< SBPixel, bp::bases<SBProfile> >("SBPixel", bp::init<const SBPixel &>())
            .def(bp::init<int, double, const InterpolantXY &, int>(
                     (bp::args("nPix", "dx", "i"), bp::arg("nImages")=1)
                 ))
            .def(bp::init<const Image<float> &, const Interpolant2d &, double, double>(
                     (bp::args("image", "i"), bp::arg("dx")=0., bp::arg("padFactor")=0.)
                 ))
            ;
    }

};

} // anonymous

void pyExportSBPixel() {
    // We wrap Interpolant classes as opaque, construct-only objects; we just
    // need to be able to make them from Python and pass them to C++.
    bp::class_<Interpolant,boost::noncopyable>("Interpolant", bp::no_init);
    bp::class_<Interpolant2d,boost::noncopyable>("Interpolant2d", bp::no_init);
    bp::class_<InterpolantXY,bp::bases<Interpolant2d>,boost::noncopyable>(
        "InterpolantXY",
        bp::init<const Interpolant &>(bp::arg("i1d"))[
            bp::with_custodian_and_ward<1,2>() // keep i1d arg alive as long as self is alive
        ]
    );
    bp::class_<Nearest,bp::bases<Interpolant>,boost::noncopyable>(
        "Nearest", bp::init<double>(bp::arg("tol")=1E-3)
    );
    bp::class_<SincInterpolant,bp::bases<Interpolant>,boost::noncopyable>(
        "SincInterpolant", bp::init<double>(bp::arg("tol")=1E-3)
    );
    bp::class_<Linear,bp::bases<Interpolant>,boost::noncopyable>(
        "Linear", bp::init<double>(bp::arg("tol")=1E-3)
    );
    bp::class_<Lanczos,bp::bases<Interpolant>,boost::noncopyable>(
        "Lanczos", bp::init<int,bool,double>(
            (bp::arg("n"), bp::arg("fluxConserve")=false, bp::arg("tol")=1E-3)
        )
    );
    bp::class_<Cubic,bp::bases<Interpolant>,boost::noncopyable>(
        "Cubic", bp::init<double>(bp::arg("tol")=1E-4)
    );
    bp::class_<Quintic,bp::bases<Interpolant>,boost::noncopyable>(
        "Quintic", bp::init<double>(bp::arg("tol")=1E-4)
    );

    PySBPixel::wrap();
}

} // namespace galsim
