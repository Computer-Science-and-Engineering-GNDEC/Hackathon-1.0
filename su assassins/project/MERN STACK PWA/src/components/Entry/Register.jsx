import React, { useState, useContext } from "react";
import Preloader from "../Dashboard/Common/Preloader";
import Header from "./Login/Header";
import { useHistory } from "react-router-dom";
import UserContext from "../../context/UserContext";
import Axios from "axios";
import ErrorNotice from "../misc/errorNotice";
import usePasswordToggle from "../misc/usePasswordToggle";

function Register() {
  const [zoho_mail, setZohomail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordCheck, setPasswordCheck] = useState("");
  const [fname, setFirstname] = useState("");
  const [lname, setLastname] = useState("");
  const [contact, setContact] = useState("");
  const [gender, setGender] = useState("");
  const [error, setError] = useState("");

  const { setUserData } = useContext(UserContext);
  const history = useHistory();

  const [passwordInputType, ToggleIcon] = usePasswordToggle();

  const submit = async (e) => {
    e.preventDefault();

    try {
      const newUser = {
        fname,
        lname,
        zoho_mail,
        contact,
        gender,
        password,
      };
      await Axios.post("/api/users", newUser);
      const loginRes = await Axios.post("/api/auth", {
        zoho_mail,
        password,
      });
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
    <React.Fragment>
      <Preloader />
      <Header />
      <div>
        <div className="page-wrapper pa-0 ma-0 auth-page">
          <div className="container-fluid">
            <div className="table-struct full-width full-height">
              <div className="table-cell vertical-align-middle auth-form-wrap">
                <div className="auth-form  ml-auto mr-auto no-float">
                  <div className="row">
                    <div className="col-sm-12 col-xs-12">
                      <div className="mb-30">
                        <h3 className="text-center txt-dark mb-10">
                          Register to Dashboard
                        </h3>
                        <h6 className="text-center nonecase-font txt-grey">
                          Enter your details below
                        </h6>
                      </div>

                      <form className="form-wrap form" onSubmit={submit}>
                        <div className="form-group">
                          <label
                            className="control-label mb-10"
                            htmlFor="exampleInputName_0"
                          >
                            First Name
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="exampleInputName_0"
                            placeholder="Enter First Name"
                            value={fname}
                            onChange={(e) => setFirstname(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label
                            className="control-label mb-10"
                            htmlFor="exampleInputName_1"
                          >
                            Last Name
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="exampleInputName_1"
                            placeholder="Enter Last Name"
                            value={lname}
                            onChange={(e) => setLastname(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label
                            className="control-label mb-10"
                            htmlFor="exampleInputEmail_2"
                          >
                            Zoho Mail
                          </label>
                          <input
                            type="email"
                            className="form-control"
                            id="exampleInputEmail_2"
                            placeholder="username@zohomail.eu"
                            value={zoho_mail}
                            onChange={(e) => setZohomail(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label
                            className="control-label mb-10"
                            htmlFor="exampleInputContact_3"
                          >
                            Contact
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="exampleInputContact_3"
                            placeholder="Contact no."
                            value={contact}
                            onChange={(e) => setContact(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label
                            className="control-label mb-10"
                            htmlFor="exampleInputGender_4"
                          >
                            Gender
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="exampleInputGender_4"
                            placeholder="Male/Female"
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
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
                          <input
                            type={passwordInputType}
                            className="form-control"
                            id="exampleInputpwd_2"
                            placeholder="Enter pwd"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                          />
                          <span className="password-icon">{ToggleIcon}</span>
                        </div>
                        <div className="form-group password-layover">
                          <label
                            className="pull-left control-label mb-10"
                            htmlFor="exampleInputpwd_3"
                          >
                            Confirm Password
                          </label>
                          <input
                            type={passwordInputType}
                            className="form-control"
                            id="exampleInputpwd_3"
                            placeholder="Enter pwd"
                            value={passwordCheck}
                            onChange={(e) => setPasswordCheck(e.target.value)}
                            required
                          />
                          <span className="password-icon">{ToggleIcon}</span>
                        </div>
                        <div className="form-group">
                          <div className="checkbox checkbox-primary pr-10 pull-left">
                            <input id="checkbox_2" type="checkbox" required />
                            <label htmlFor="checkbox_2">
                              {" "}
                              I agree to all{" "}
                              <span className="txt-primary">Terms</span>
                            </label>
                          </div>
                          <div className="clearfix"></div>
                        </div>
                        <div className="form-group text-center">
                          <button
                            type="submit"
                            className="btn btn-info btn-success btn-rounded"
                            value="Register"
                          >
                            Register
                          </button>
                        </div>
                      </form>
                      {error && (
                        <ErrorNotice
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
    </React.Fragment>
  );
}

export default Register;
