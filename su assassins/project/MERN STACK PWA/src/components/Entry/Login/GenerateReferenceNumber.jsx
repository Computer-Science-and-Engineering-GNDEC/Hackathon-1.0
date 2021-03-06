import React, { useState } from "react";
import Header from "./Header";
import ErrorNotice from "../../misc/errorNotice";

function ForgotPassword() {
  const [internEmail, setInternEmail] = useState();
  const [error, setError] = useState();

  return (
    <div className="wrapper pa-0">
      <Header />
      <div className="page-wrapper pa-0 ma-0 auth-page">
        <div className="container-fluid">
          <div className="table-struct full-width full-height">
            <div
              className="table-cell vertical-align-middle auth-form-wrap"
              style={{ height: "100vh" }}
            >
              <div className="auth-form ml-auto mr-auto no-float">
                <div className="row">
                  <div className="col-sm-12 col-xs-12 ">
                    {error && (
                      <ErrorNotice
                        message={error}
                        clearError={() => setError(undefined)}
                      />
                    )}
                    <form className="form-wrap form">
                      <div className="form-group text-center">
                        <button
                          type="submit"
                          className="btn btn-info btn-success btn-rounded mb-10 "
                          value="submit"
                        >
                          Generate Reference Number
                        </button>
                        <br />
                        <label
                          className=" control-label mb-10 pull-left"
                          htmlFor="generated_reference_number"
                        >
                          Reference Number:
                        </label>
                        <input
                          type="email"
                          className="form-control  mb-10 text-center"
                          id="exampleInputEmail_2"
                          placeholder="Enter Intern's Zoho Mail"
                          value={internEmail}
                          onChange={(e) => setInternEmail(e.target.value)}
                          required
                        />
                        <button
                          type="submit"
                          className="btn btn-info btn-success btn-rounded"
                          value="submit"
                        >
                          Send Email
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
