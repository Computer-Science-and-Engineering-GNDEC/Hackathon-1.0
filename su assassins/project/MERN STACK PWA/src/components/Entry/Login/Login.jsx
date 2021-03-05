import React, { useState, useContext } from "react";
import Header from "./Header";
import { Link, useHistory } from "react-router-dom";
import Axios from "axios";
import UserContext from "../../../context/UserContext";
import ErrorNotice from "../../misc/errorNotice";
import usePasswordToggle from "../../misc/usePasswordToggle";

import LoginSvg from "../../../assets/login.svg";

import "./login.css";

function Login() {
  const [zoho_mail, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { setUserData } = useContext(UserContext);
  const history = useHistory();

  const [passwordInputType, ToggleIcon] = usePasswordToggle();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const loginUser = { zoho_mail, password };
      const loginRes = await Axios.post("/api/auth/", loginUser);
      setUserData({
        token: loginRes.data.token,
        user: loginRes.data.user,
      });
      localStorage.setItem("auth-token", loginRes.data.token);
      history.push("/");
    } catch (err) {
      const errors = err.response.data.errors;
      errors.forEach((error) => setError(error.msg));
    }
  };

  return (
    <div className="wrapper pa-0">
      <Header />
      <div className="page-wrapper pa-0 ma-0 auth-page login">
        <div className="container-fluid">
          <div className="table-struct full-width full-height">
            <div
              className="table-cell vertical-align-middle auth-form-wrap"
              style={{ height: "100vh" }}
            >
              <div className="auth-form ml-auto mr-auto no-float">
                <div className="row">
                  <div className="col-sm-12 col-xs-12">
                    <div className="mb-30">
                      {/* <h3 className="text-center txt-dark mb-10">
                        Sign in to LSCG
                      </h3> */}
                    </div>
                    {error && (
                      <ErrorNotice
                        message={error}
                        clearError={() => setError(undefined)}
                      />
                    )}

                    <div className="row">
                      <div className="col-lg-6">
                        <img src={LoginSvg} alt="login" className="login-svg" />
                      </div>
                      <div className="col-lg-6">
                        <h3 className="text-center">
                          Sign in to Dashboard
                        </h3>
                        <h6 className="text-center nonecase-font txt-grey">
                          Enter your details below
                        </h6>
                        <br />
                        <form className="form-wrap form" onSubmit={submit}>
                          <div className="form-group">
                            <label
                              className="pull-left control-label mb-10"
                              htmlFor="exampleInputEmail_2"
                            >
                              E-Mail
                            </label>
                            <input
                              type="email"
                              className="form-control"
                              id="exampleInputEmail_2"
                              placeholder="Enter e-mail (Zoho Mail)"
                              value={zoho_mail}
                              onChange={(e) => setUsername(e.target.value)}
                              required
                            />
                          </div>
                          <div className="form-group password-layover">
                            <label
                              className="pull-left control-label mb-10"
                              htmlFor="exampleInputpwd_2"
                            >
                              Password
                            </label>

                            <Link
                              className="capitalize-font txt-primary block mb-10 pull-right font-12"
                              to="/forgot"
                            >
                              forgot password ?
                            </Link>
                            <div className="clearfix"></div>
                            <input
                              type={passwordInputType}
                              className="form-control"
                              id="exampleInputpwd_2"
                              placeholder="Enter password"
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              required
                            />
                            <span className="password-icon">{ToggleIcon}</span>
                          </div>

                          <div className="form-group">
                            <div className="checkbox checkbox-primary pr-10 pull-left">
                              <input
                                id="checkbox_2"
                                required=""
                                type="checkbox"
                              />
                              <label htmlFor="checkbox_2">
                                {" "}
                                Keep me logged in
                              </label>
                            </div>
                            <div className="clearfix"></div>
                          </div>
                          <div className="form-group text-center">
                            <button
                              type="submit"
                              className="btn btn-info btn-success btn-rounded"
                              value="Login"
                            >
                              Login
                            </button>
                            <br />
                            <br />
                            {/* <button
                          type="submit"
                          className="btn btn-info btn-success btn-rounded"
                        >
                          sign in with Linkedin
                        </button> */}
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
      </div>
    </div>
  );
}

export default Login;
