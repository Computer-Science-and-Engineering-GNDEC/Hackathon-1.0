import React from "react";
import { Link } from "react-router-dom";

const NotFoundPage = () => (
  <div cz-shortcut-listen="true">
    <div class="preloader-it" style={{ display: "none" }}>
      <div class="la-anim-1 la-animate"></div>
    </div>

    <div class="wrapper error-page pa-0">
      <header class="sp-header">
        <div class="sp-logo-wrap pull-left">
          <a href="/">
            <img
              className="brand-img mr-10"
              src="dist/images/logo.png"
              alt="brand"
              height="50px"
              width="180px"
            />
          </a>
        </div>
        <div class="form-group mb-0 pull-right">
          <a
            class="inline-block btn btn-success btn-rounded btn-outline nonecase-font"
            href="/"
          >
            Back to Home
          </a>
        </div>
        <div class="clearfix"></div>
      </header>

      <div
        class="page-wrapper pa-0 ma-0 error-bg-img"
        style={{ height: "800px" }}
      >
        <div class="container-fluid">
          <div
            class="table-struct full-width full-height"
            style={{ height: "800px" }}
          >
            <div class="table-cell vertical-align-middle auth-form-wrap">
              <div class="auth-form  ml-auto mr-auto no-float">
                <div class="row">
                  <div class="col-sm-12 col-xs-12">
                    <div class="mb-30">
                      <span class="block error-head text-center txt-success mb-10">
                        404
                      </span>
                      <span class="text-center nonecase-font mb-20 block error-comment">
                        Page Not Found
                      </span>
                      <p class="text-center">
                        The URL may be misplaced or the pahe you are looking is
                        no longer available.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default NotFoundPage;
