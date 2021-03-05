import React, { useState, useEffect } from "react";
import Preloader from "../Dashboard/Common/Preloader";
import Header from "./Login/Header";
import { useHistory } from "react-router-dom";
// import UserContext from "../../context/UserContext";
import Axios from "axios";
import ErrorNotice from "../misc/errorNotice";
import usePasswordToggle from "../misc/usePasswordToggle";

function ResetPass({ match }) {
  const [password, setPassword] = useState("");
  const [passwordCheck, setPasswordCheck] = useState("");

  const [error, setError] = useState();

  const history = useHistory();

  const [passwordInputType, ToggleIcon] = usePasswordToggle();

  const [isReset, setIsReset] = useState(false);

  // console.log("props", props);

  useEffect(() => {
    const pageVal = async () => {
      try {
        const res = await Axios.get(`/api/auth/reset/${match.params.token}`);
        console.log("checkVal", res);
      } catch (err) {
        console.log(err);
        // setIsReset(true);
        history.push("/notfound");
        // history.go();
      }
    };
    pageVal();
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    if (password !== passwordCheck) {
      setError("Passwords do not match");
    } else {
      try {
        const res = await Axios.post(
          `/api/auth/reset/${match.params.token}`,
          {
            password: password,
          },
          {
            "Content-Type": "application/json",
          }
        );
        console.log(res);
        if (res.status === 200) {
          setIsReset(true);
        }
      } catch (err) {
        console.log(err);
      }
    }
  };

  return (
    <React.Fragment>
      <Preloader />
      <Header />
      <div>
        <div
          className="page-wrapper pa-0 ma-0 auth-page"
          style={{
            height: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {isReset ? (
            <h3>Your password has been reset</h3>
          ) : (
            <div className="container-fluid">
              <div className="table-struct full-width full-height">
                <div className="table-cell vertical-align-middle auth-form-wrap">
                  <div className="auth-form  ml-auto mr-auto no-float">
                    <div className="row">
                      <div className="col-sm-12 col-xs-12">
                        <div className="mb-30">
                          <h3 className="text-center txt-dark mb-10">
                            Reset Password
                          </h3>
                          <h6 className="text-center nonecase-font txt-grey">
                            Enter your details below
                          </h6>
                        </div>
                        {error && (
                          <ErrorNotice
                            message={error}
                            clearError={() => setError(undefined)}
                          />
                        )}
                        <form className="form-wrap form" onSubmit={submit}>
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

                          <div className="form-group text-center">
                            <button
                              type="submit"
                              className="btn btn-info btn-success btn-rounded"
                              value="ResetPass"
                            >
                              ResetPass
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </React.Fragment>
  );
}

export default ResetPass;
