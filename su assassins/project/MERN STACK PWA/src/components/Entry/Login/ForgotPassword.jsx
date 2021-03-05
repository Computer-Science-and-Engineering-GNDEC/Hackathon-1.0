import React, { useState } from "react";
import Header from "./Header";
import ErrorNotice from "../../misc/errorNotice";
import Axios from "axios";

function ForgotPassword() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  const [errorStatus, setErrorStatus] = useState(false);

  const handleClick = async (e) => {
    e.preventDefault();

    try {
      const res = await Axios.post(
        `/api/auth/forgot-password`,
        {
          zoho_mail: username,
        },
        {
          "Content-Type": "application/json",
        }
      );
      console.log(res);
      setError(res.data.message);
      setErrorStatus(true);
    } catch (err) {
      console.log(err.response);
      const { errors } = err.response.data;
      errors.forEach((er) => {
        setError(er.msg);
      });
      // setError(err.response.data.errors);
    }
  };

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
              <div className="auth-form  ml-auto mr-auto no-float">
                <div className="row">
                  <div className="col-sm-12 col-xs-12">
                    <form className="form-wrap form">
                      <div className="form-group text-center">
                        <label
                          className="control-label mb-10"
                          htmlFor="exampleInputEmail_2"
                        >
                          <h4 className="text-center">Forgot Password</h4>
                          <br />
                        </label>
                        <input
                          type="email"
                          className="form-control  mb-10 my-4"
                          id="exampleInputEmail_2"
                          placeholder="Enter zoho mail"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          required
                        />
                        <br />
                        <button
                          type="submit"
                          className="btn btn-info btn-success btn-rounded d-block mx-auto"
                          value="submit"
                          onClick={handleClick}
                        >
                          Submit
                        </button>
                      </div>
                    </form>
                    {error && (
                      <ErrorNotice
                        status={errorStatus}
                        message={error}
                        clearError={() => setError(undefined)}
                      />
                    )}
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
