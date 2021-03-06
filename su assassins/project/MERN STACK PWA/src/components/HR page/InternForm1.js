import React, { useState } from "react";
import Preloader from "../Dashboard/Common/Preloader";
import Header from "../Entry/Login/Header";
import moment from "moment";
import uid from "uid";
import "react-dates/initialize";
import { DateRangePicker } from "react-dates";
import "react-dates/lib/css/_datepicker.css";

const InternForm1 = () => {
  const [name, setname] = useState("");
  const [FatherName, setFatherName] = useState("");
  const [gender, setgender] = useState("");
  const [LinkedIn, setLinkedIn] = useState("");
  const [email, setemail] = useState("");
  const [ZohoMail, setZohoMail] = useState("");
  const[number,setnumber ] = useState();
  const [address, setaddress] = useState("");
  const [InstitituionName, setInstitituionName] = useState("");
  const [qualification, setqualification] = useState("");
  const [error, seterror] = useState("");
 

  const onSubmit = (e) => {
    e.preventDefault();

    if (!this.state.name || !this.state.email) {
      seterror(() => ({
        error: "Please provide all the information",
      }));
    } else {
      this.seterror(() => ({ error: "" }));
      this.props.onSubmit({
        name: this.state.name,
        gender: this.state.gender,
        email: JSON.stringify(this.state.email),
        address: this.state.address,
        startDate: this.state.startDate.valueOf(),
        endDate: this.state.endDate.valueOf(),
      });
    }
  };
   return(
    <React.Fragment>
    <Preloader />
    <Header />
    <div className="wrapper theme-1-active box-layout pimary-color-green">
      <div className="container-fluid">
        <div className="table-struct full-width full-height">
          <div className="row heading-bg"></div>

          <div className="row">
            <div className="col-sm-12">
              <div className="panel panel-default card-view">
                <div className="panel-heading">
                  <div className="pull-left">
                    <h6 className="panel-title txt-dark">Candidate Information Form</h6>
                  </div>
                  <div className="clearfix"></div>
                </div>
                <div className="panel-wrapper collapse in">
                  <div className="panel-body">
                    <div className="form-wrap">
                      <form onSubmit={onSubmit}>
                      <div class="form-group">
													<label className="control-label mb-10">Post Applied for</label>
													<select className="form-control select2 select2-hidden-accessible" tabindex="-1" aria-hidden="true">
														<option>Select</option>
														<optgroup label="Alaskan/Hawaiian Time Zone">
															<option value="AK">Alaska</option>
															<option value="HI">Hawaii</option>
														</optgroup>
														<optgroup label="Pacific Time Zone">
															<option value="CA">California</option>
															<option value="NV">Nevada</option>
															<option value="OR">Oregon</option>
															<option value="WA">Washington</option>
														</optgroup>
														<optgroup label="Mountain Time Zone">
															<option value="AZ">Arizona</option>
															<option value="CO">Colorado</option>
															<option value="ID">Idaho</option>
															<option value="MT">Montana</option>
															<option value="NE">Nebraska</option>
															<option value="NM">New Mexico</option>
															<option value="ND">North Dakota</option>
															<option value="UT">Utah</option>
															<option value="WY">Wyoming</option>
														</optgroup>
														<optgroup label="Central Time Zone">
															<option value="AL">Alabama</option>
															<option value="AR">Arkansas</option>
															<option value="IL">Illinois</option>
															<option value="IA">Iowa</option>
															<option value="KS">Kansas</option>
															<option value="KY">Kentucky</option>
															<option value="LA">Louisiana</option>
															<option value="MN">Minnesota</option>
															<option value="MS">Mississippi</option>
															<option value="MO">Missouri</option>
															<option value="OK">Oklahoma</option>
															<option value="SD">South Dakota</option>
															<option value="TX">Texas</option>
															<option value="TN">Tennessee</option>
															<option value="WI">Wisconsin</option>
														</optgroup>
														<optgroup label="Eastern Time Zone">
															<option value="CT">Connecticut</option>
															<option value="DE">Delaware</option>
															<option value="FL">Florida</option>
															<option value="GA">Georgia</option>
															<option value="IN">Indiana</option>
															<option value="ME">Maine</option>
															<option value="MD">Maryland</option>
															<option value="MA">Massachusetts</option>
															<option value="MI">Michigan</option>
															<option value="NH">New Hampshire</option>
															<option value="NJ">New Jersey</option>
															<option value="NY">New York</option>
															<option value="NC">North Carolina</option>
															<option value="OH">Ohio</option>
															<option value="PA">Pennsylvania</option>
															<option value="RI">Rhode Island</option>
															<option value="SC">South Carolina</option>
															<option value="VT">Vermont</option>
															<option value="VA">Virginia</option>
															<option value="WV">West Virginia</option>
														</optgroup>
													</select><span class="select2 select2-container select2-container--default select2-container--below" dir="ltr" style={{width: "578px"}}><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-d1e6-container"><span class="select2-selection__rendered" id="select2-d1e6-container" title="Select">Select</span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
                        </div>

                          <div class="form-group">
                            <label class="btn-group bootstrap-select">Duration of Internship</label>
                            <div class="btn-group bootstrap-select dropup"><button type="button" className="btn dropdown-toggle form-control btn-default btn-outline" data-toggle="dropdown" role="button" title="Relish" aria-expanded="false"><span class="filter-option pull-left">Relish</span>&nbsp;<span class="bs-caret"><span class="caret"></span></span></button><div class="dropdown-menu open" role="combobox" style={{maxheight: "297.6px"}}><ul class="dropdown-menu inner" role="listbox" aria-expanded="false" style={{maxheight: "287.6px"}}><li data-original-index="0" class="ms-hover"><a tabindex="0" data-tokens="null" role="option" aria-disabled="false" aria-selected="false"><span class="text">Mustard</span><span class="glyphicon glyphicon-ok check-mark"></span></a></li><li data-original-index="1" class="ms-hover"><a tabindex="0" data-tokens="null" role="option" aria-disabled="false" aria-selected="false"><span className="text">Ketchup</span><span class="glyphicon glyphicon-ok check-mark"></span></a></li><li data-original-index="2" class="ms-hover selected"><a tabindex="0" data-tokens="null" role="option" aria-disabled="false" aria-selected="true"><span class="text">Relish</span><span class="glyphicon glyphicon-ok check-mark"></span></a></li></ul></div><select class="selectpicker" data-style="form-control btn-default btn-outline" tabindex="-98">
							
															</select></div>
                          </div>
                      
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                           Candidate's Full Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={name}
                            onChange={(e) => setname(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Father's Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={FatherName}
                            onChange={(e) => setFatherName(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group mb-30">
                          <label className="control-label mb-10 text-left">
                            Gender
                          </label>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="radio1"
                              value="Male"
                              checked={gender === "Male"}
                              onChange={() => setgender((gender = "Male"))}
                            />
                            <label htmlFor="radio1">Male</label>
                          </div>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="Female"
                              value="Female"
                              checked={gender === "Female"}
                              onChange={(e) => setgender(e.target.value)}
                            />
                            <label htmlFor="radio2">Female</label>
                          </div>
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Address
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Address"
                            value={address}
                            onChange={(e) => setaddress(e.target.value)}
                          />
                        </div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                            Mobile-Number
                          </label>
                          <input
                            type="Number"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Mobile Number"
                            value={number}
                            onChange={(e) => setnumber(e.target.value)}
                          />
                        </div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                            Email-id
                          </label>
                          <input
                            type="email"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setemail(e.target.value)}
                          />
                        </div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                          Linkedin URL (Please provide accurate url)*
                          </label>
                          <input
                            type="URL"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="LinkedIn-URL"
                            value={LinkedIn}
                            onChange={(e) => setLinkedIn(e.target.value)}
                          />
                        </div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                          Email associated with Linkedin userID (eg. debasis@londonscg.com).
                          Our internal application authentication will be via linkedIn*
                          </label>
                          <input
                            type="email"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Email"
                            value={ZohoMail}
                            onChange={(e) => setZohoMail(e.target.value)}
                          />
                        </div>
                        <div className="form-group mb-0">
                        <label className="control-label mb-10 text-left">
                          latest Education Qualification
                          </label>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Latest Education Qualification"
                            value={qualification}
                            onChange={(e) => setqualification(e.target.value)}
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Institution Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={InstitituionName}
                            onChange={(e) => setInstitituionName(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group mb-0">
                          <button type="button" className="btn btn-success ">
                            <span className="btn-text">submit</span>
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
    </div>
  </React.Fragment>
);
                          };
export default InternForm1;

