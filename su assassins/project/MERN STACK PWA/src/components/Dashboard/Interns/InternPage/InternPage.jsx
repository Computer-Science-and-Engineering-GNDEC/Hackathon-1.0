import React, { useEffect, useState } from "react";
import Preloader from "../../Common/Preloader";
import { Link } from "react-router-dom";
import DashHeader from "../../Common/DashHeader";
import SidebarLeft from "../../Common/SidebarLeft";
import Axios from "axios";
import { localeData } from "moment";
import { useDispatch } from "react-redux";
import { setRole } from "../../../../redux/actions/internActions";

function InternPage() {
  //Redux

  const dispatch = useDispatch();

  const [userData, setUserData] = useState({
    fname: "",
    lname: "",
    contact: "",
    gender: "",
    role: "",
    zoho_mail: "",
  });
  const [file, setFile] = useState("");

  const [fname, setFname] = useState("");
  const [lname, setLname] = useState("");
  const [contact, setContact] = useState("");
  const [gender, setGender] = useState("");
  const [zoho, setZoho] = useState("");
  const [id, setId] = useState("");
  useEffect(() => {
    const getUser = async () => {
      const token = localStorage.getItem("auth-token");
      if (token) {
        console.log(token);
      }
      try {
        const res = await Axios.get(`/api/auth/user/5fdf434ea0df98399c101efc`, {
          headers: {
            "x-auth-token": token,
          },
        });
        // localStorage.setItemauth("userID", res.data._id);

        console.log("someres", { res });

        const {
          _id,
          fname,
          lname,
          contact,
          gender,
          role,
          zoho_mail,
        } = res.data;
        // setUserData({ fname: fname });
        setFname(fname);
        setLname(lname);
        setContact(contact);
        setGender(gender);
        setZoho(zoho_mail);
        setId(_id);
        dispatch(setRole(role));
        console.log({ role });
      } catch (error) {
        console.log(error.response);
      }
    };

    getUser();
  }, [fname, lname, contact, gender, zoho]);

  const uploadPP = async (e) => {
    e.preventDefault();
    setFile(e.target.files[0]);
    console.log(e.target.files[0].name);

    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("auth-token");

    try {
      const res = await Axios.post("/api/profilepic/upload", formData, {
        headers: {
          "x-auth-token": token,
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (ProgressEvent) => {
          if (ProgressEvent.loaded) {
            console.log("lets see");
          }
        },
      });

      setFile("");
      console.log(res.data);
    } catch (err) {
      setFile("");
      console.log(err.response.data);
    }
  };

  return (
    <React.Fragment>
      <Preloader />
      <div className="wrapper theme-1-active box-layout pimary-color-green">
        <DashHeader />
        {/* Left Sidebar Menu */}
        <SidebarLeft />
        {/* /Left Sidebar Menu */}

        {/* Right Sidebar Menu */}
        <div className="fixed-sidebar-right">
          <ul className="right-sidebar">
            <li>
              <div className="tab-struct custom-tab-1">
                <ul
                  role="tablist"
                  className="nav nav-tabs"
                  id="right_sidebar_tab"
                >
                  <li className="active" role="presentation">
                    <Link
                      aria-expanded="true"
                      data-toggle="tab"
                      role="tab"
                      id="chat_tab_btn"
                      to="#chat_tab"
                    >
                      chat
                    </Link>
                  </li>
                  <li role="presentation" className="">
                    <Link
                      data-toggle="tab"
                      id="messages_tab_btn"
                      role="tab"
                      to="#messages_tab"
                      aria-expanded="false"
                    >
                      messages
                    </Link>
                  </li>
                  <li role="presentation" className="">
                    <Link
                      data-toggle="tab"
                      id="todo_tab_btn"
                      role="tab"
                      to="#todo_tab"
                      aria-expanded="false"
                    >
                      todo
                    </Link>
                  </li>
                </ul>
                <div className="tab-content" id="right_sidebar_content">
                  <div
                    id="chat_tab"
                    className="tab-pane fade active in"
                    role="tabpanel"
                  >
                    <div className="chat-cmplt-wrap">
                      <div className="chat-box-wrap">
                        <div className="add-friend">
                          <Link to="" className="inline-block txt-grey">
                            <i className="zmdi zmdi-more"></i>
                          </Link>
                          <span className="inline-block txt-dark">users</span>
                          <Link
                            to=""
                            className="inline-block text-right txt-grey"
                          >
                            <i className="zmdi zmdi-plus"></i>
                          </Link>
                          <div className="clearfix"></div>
                        </div>
                        <form
                          role="search"
                          className="chat-search pl-15 pr-15 pb-15"
                        >
                          <div className="input-group">
                            <input
                              type="text"
                              id="example-input1-group2"
                              name="example-input1-group2"
                              className="form-control"
                              placeholder="Search"
                            />
                            <span className="input-group-btn">
                              <button
                                type="button"
                                className="btn  btn-default"
                              >
                                <i className="zmdi zmdi-search"></i>
                              </button>
                            </span>
                          </div>
                        </form>
                        <div id="chat_list_scroll">
                          <div className="nicescroll-bar">
                            <ul className="chat-list-wrap">
                              <li className="chat-list">
                                <div className="chat-body">
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          {fname} {lname}
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          No one saves us but ourselves.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user1.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Evie Ono
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Unity is strength
                                        </span>
                                      </div>
                                      <div className="status offline"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user2.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Madalyn Rascon
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Respect yourself if you would have
                                          others respect you.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user3.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Mitsuko Heid
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          I’m thankful.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Ezequiel Merideth
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Patience is bitter.
                                        </span>
                                      </div>
                                      <div className="status offline"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user1.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Jonnie Metoyer
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Genius is eternal patience.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user2.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Angelic Lauver
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Every burden is a blessing.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user3.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Priscila Shy
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Wise to resolve, and patient to
                                          perform.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                  <Link to="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user4.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Linda Stack
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Our patience will achieve more than
                                          our force.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </Link>
                                </div>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>
                      <div className="recent-chat-box-wrap">
                        <div className="recent-chat-wrap">
                          <div className="panel-heading ma-0">
                            <div className="goto-back">
                              <Link
                                id="goto_back"
                                to=""
                                className="inline-block txt-grey"
                              >
                                <i className="zmdi zmdi-chevron-left"></i>
                              </Link>
                              <span className="inline-block txt-dark">
                                ryan
                              </span>
                              <Link
                                to=""
                                className="inline-block text-right txt-grey"
                              >
                                <i className="zmdi zmdi-more"></i>
                              </Link>
                              <div className="clearfix"></div>
                            </div>
                          </div>
                          <div className="panel-wrapper collapse in">
                            <div className="panel-body pa-0">
                              <div className="chat-content">
                                <ul className="nicescroll-bar pt-20">
                                  <li className="friend">
                                    <div className="friend-msg-wrap">
                                      <img
                                        className="user-img img-circle block pull-left"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="msg pull-left">
                                        <p>
                                          Hello Jason, how are you, it's been a
                                          long time since we last met?
                                        </p>
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:30 PM
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="self mb-10">
                                    <div className="self-msg-wrap">
                                      <div className="msg block pull-right">
                                        {" "}
                                        Oh, hi Sarah I'm have got a new job now
                                        and is going great.
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:31 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="self">
                                    <div className="self-msg-wrap">
                                      <div className="msg block pull-right">
                                        {" "}
                                        How about you?
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:31 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="friend">
                                    <div className="friend-msg-wrap">
                                      <img
                                        className="user-img img-circle block pull-left"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="msg pull-left">
                                        <p>Not too bad.</p>
                                        <div className="msg-per-detail  text-right">
                                          <span className="msg-time txt-grey">
                                            2:35 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                </ul>
                              </div>
                              <div className="input-group">
                                <input
                                  type="text"
                                  id="input_msg_send"
                                  name="send-msg"
                                  className="input-msg-send form-control"
                                  placeholder="Type something"
                                />
                                <div className="input-group-btn emojis">
                                  <div className="dropup">
                                    <button
                                      type="button"
                                      className="btn  btn-default  dropdown-toggle"
                                      data-toggle="dropdown"
                                    >
                                      <i className="zmdi zmdi-mood"></i>
                                    </button>
                                    <ul className="dropdown-menu dropdown-menu-right">
                                      <li>
                                        <Link to="">Action</Link>
                                      </li>
                                      <li>
                                        <Link to="">Another action</Link>
                                      </li>
                                      <li className="divider"></li>
                                      <li>
                                        <Link to="">Separated link</Link>
                                      </li>
                                    </ul>
                                  </div>
                                </div>
                                <div className="input-group-btn attachment">
                                  <div className="fileupload btn  btn-default">
                                    <i className="zmdi zmdi-attachment-alt"></i>
                                    <input type="file" className="upload" />
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
              </div>
            </li>
          </ul>
        </div>
        {/* /Right Sidebar Manu */}

        {/* Right Sidebar Backdrop */}
        <div className="right-sidebar-backdrop"></div>
        {/* /Right Sidebar Backdrop */}

        {/* <!-- Main Content --> */}
        <div className="page-wrapper">
          <div className="container-fluid pt-25">
            {/* <!-- Row --> */}
            <div className="row">
              <div className="col-lg-3 col-xs-12">
                <div className="panel panel-default card-view  pa-0">
                  <div className="panel-wrapper collapse in">
                    <div className="panel-body  pa-0">
                      <div className="profile-box">
                        <div className="profile-cover-pic">
                          <div className="fileupload btn btn-default">
                            <span className="btn-text">edit</span>
                            <input className="upload" type="file" />
                          </div>
                          <div className="profile-image-overlay"></div>
                        </div>
                        <div className="profile-info text-center">
                          <div className="profile-img-wrap">
                            <img
                              className="inline-block mb-10"
                              src={`uploads/${id}.jpg` || "dist/img/user.png"}
                              alt="user"
                            />
                            <div className="fileupload btn btn-default">
                              <span className="btn-text">edit</span>
                              <input
                                className="upload"
                                type="file"
                                onChange={uploadPP}
                              />
                            </div>
                          </div>
                          <h5 className="block mt-10 mb-5 weight-500 capitalize-font txt-danger">
                            {fname} {lname}
                          </h5>
                          <h6 className="block capitalize-font pb-20">
                            Delivery Lead
                          </h6>
                        </div>
                        <div className="social-info">
                          <div className="row">
                            <div className="col-xs-4 text-center">
                              <span className="counts block head-font">
                                <span className="counter-anim">0</span>
                              </span>
                              <span className="counts-text block">
                                activity
                              </span>
                            </div>
                            <div className="col-xs-4 text-center">
                              <span className="counts block head-font">
                                <span className="counter-anim">0</span>
                              </span>
                              <span className="counts-text block">
                                contacts
                              </span>
                            </div>
                            <div className="col-xs-4 text-center">
                              <span className="counts block head-font">
                                <span className="counter-anim">0</span>
                              </span>
                              <span className="counts-text block">
                                projects
                              </span>
                            </div>
                          </div>
                          {/* <button
                            className="btn btn-default btn-block btn-outline btn-anim mt-30"
                            data-toggle="modal"
                            data-target="#myModal"
                          >
                            <i className="fa fa-pencil"></i>
                            <span className="btn-text">edit profile</span>
                          </button> */}
                          <div
                            id="myModal"
                            className="modal fade in"
                            tabindex="-1"
                            role="dialog"
                            aria-labelledby="myModalLabel"
                            aria-hidden="true"
                          >
                            <div className="modal-dialog">
                              <div className="modal-content">
                                <div className="modal-header">
                                  <button
                                    type="button"
                                    className="close"
                                    data-dismiss="modal"
                                    aria-hidden="true"
                                  >
                                    ×
                                  </button>
                                  <h5 className="modal-title" id="myModalLabel">
                                    Edit Profile
                                  </h5>
                                </div>
                                <div className="modal-body">
                                  {/* <!-- Row --> */}
                                  <div className="row">
                                    <div className="col-lg-12">
                                      <div className="">
                                        <div className="panel-wrapper collapse in">
                                          <div className="panel-body pa-0">
                                            <div className="col-sm-12 col-xs-12">
                                              <div className="form-wrap">
                                                <form action="#">
                                                  <div className="form-body overflow-hide">
                                                    <div className="form-group">
                                                      <label
                                                        className="control-label mb-10"
                                                        htmlFor="exampleInputuname_1"
                                                      >
                                                        Name
                                                      </label>
                                                      <div className="input-group">
                                                        <div className="input-group-addon">
                                                          <i className="icon-user"></i>
                                                        </div>
                                                        <input
                                                          type="text"
                                                          className="form-control"
                                                          id="exampleInputuname_1"
                                                          placeholder="willard bryant"
                                                        />
                                                      </div>
                                                    </div>
                                                    <div className="form-group">
                                                      <label
                                                        className="control-label mb-10"
                                                        htmlFor="exampleInputEmail_1"
                                                      >
                                                        Email address
                                                      </label>
                                                      <div className="input-group">
                                                        <div className="input-group-addon">
                                                          <i className="icon-envelope-open"></i>
                                                        </div>
                                                        <input
                                                          type="email"
                                                          className="form-control"
                                                          id="exampleInputEmail_1"
                                                          placeholder="xyz@gmail.com"
                                                        />
                                                      </div>
                                                    </div>
                                                    <div className="form-group">
                                                      <label
                                                        className="control-label mb-10"
                                                        htmlFor="exampleInputContact_1"
                                                      >
                                                        Contact number
                                                      </label>
                                                      <div className="input-group">
                                                        <div className="input-group-addon">
                                                          <i className="icon-phone"></i>
                                                        </div>
                                                        <input
                                                          type="email"
                                                          className="form-control"
                                                          id="exampleInputContact_1"
                                                          placeholder="+102 9388333"
                                                        />
                                                      </div>
                                                    </div>
                                                    <div className="form-group">
                                                      <label
                                                        className="control-label mb-10"
                                                        htmlFor="exampleInputpwd_1"
                                                      >
                                                        Password
                                                      </label>
                                                      <div className="input-group">
                                                        <div className="input-group-addon">
                                                          <i className="icon-lock"></i>
                                                        </div>
                                                        <input
                                                          type="password"
                                                          className="form-control"
                                                          id="exampleInputpwd_1"
                                                          placeholder="Enter pwd"
                                                          value="password"
                                                        />
                                                      </div>
                                                    </div>
                                                    <div className="form-group">
                                                      <label className="control-label mb-10">
                                                        Gender
                                                      </label>
                                                      <div>
                                                        <div className="radio">
                                                          <input
                                                            type="radio"
                                                            name="radio1"
                                                            id="radio_1"
                                                            value="option1"
                                                            checked=""
                                                          />
                                                          <label htmlFor="radio_1">
                                                            M
                                                          </label>
                                                        </div>
                                                        <div className="radio">
                                                          <input
                                                            type="radio"
                                                            name="radio1"
                                                            id="radio_2"
                                                            value="option2"
                                                          />
                                                          <label htmlFor="radio_2">
                                                            F
                                                          </label>
                                                        </div>
                                                      </div>
                                                    </div>
                                                    <div className="form-group">
                                                      <label className="control-label mb-10">
                                                        Country
                                                      </label>
                                                      <select
                                                        className="form-control"
                                                        data-placeholder="Choose a Category"
                                                        tabindex="1"
                                                      >
                                                        <option value="Category 1">
                                                          USA
                                                        </option>
                                                        <option value="Category 2">
                                                          Austrailia
                                                        </option>
                                                        <option value="Category 3">
                                                          India
                                                        </option>
                                                        <option value="Category 4">
                                                          UK
                                                        </option>
                                                      </select>
                                                    </div>
                                                  </div>
                                                  {/* <div className="form-actions mt-10">
                                                    <button
                                                      type="submit"
                                                      className="btn btn-success mr-10 mb-30"
                                                    >
                                                      Update profile
                                                    </button>
                                                  </div> */}
                                                </form>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                <div className="modal-footer">
                                  <button
                                    type="button"
                                    className="btn btn-success waves-effect"
                                    data-dismiss="modal"
                                  >
                                    Save
                                  </button>
                                  <button
                                    type="button"
                                    className="btn btn-default waves-effect"
                                    data-dismiss="modal"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                              {/* <!-- /.modal-content --> */}
                            </div>
                            {/* <!-- /.modal-dialog --> */}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-lg-9 col-xs-12">
                <div className="panel panel-default card-view pa-0">
                  <div className="panel-wrapper collapse in">
                    <div className="panel-body pb-0">
                      <div className="tab-struct custom-tab-1">
                        <ul
                          role="tablist"
                          className="nav nav-tabs nav-tabs-responsive"
                          id="myTabs_8"
                        >
                          <li className="active" role="presentation">
                            <Link
                              data-toggle="tab"
                              id="settings_tab_8"
                              role="tab"
                              to="#settings_8"
                              aria-expanded="false"
                            >
                              <span>profile</span>
                            </Link>
                          </li>
                          <li role="presentation" className="next">
                            <Link
                              aria-expanded="true"
                              data-toggle="tab"
                              role="tab"
                              id="follo_tab_8"
                              to="#follo_8"
                            >
                              <span>
                                contacts
                                <span className="inline-block">(246)</span>
                              </span>
                            </Link>
                          </li>
                          <li role="presentation" className="">
                            <Link
                              data-toggle="tab"
                              id="profile_tab_8"
                              role="tab"
                              to="#profile_8"
                              aria-expanded="false"
                            >
                              <span>activities</span>
                            </Link>
                          </li>
                          <li role="presentation" className="">
                            <Link
                              data-toggle="tab"
                              id="earning_tab_8"
                              role="tab"
                              to="#earnings_8"
                              aria-expanded="false"
                            >
                              <span>achievements</span>
                            </Link>
                          </li>

                          <li role="presentation" className="">
                            <Link
                              data-toggle="tab"
                              id="photos_tab_8"
                              role="tab"
                              to="#photos_8"
                              aria-expanded="false"
                            >
                              <span>files</span>
                            </Link>
                          </li>
                        </ul>
                        <div className="tab-content" id="myTabContent_8">
                          <div
                            id="profile_8"
                            className="tab-pane fade"
                            role="tabpanel"
                          >
                            <div className="col-md-12">
                              <div className="pt-20">
                                <div className="streamline user-activity">
                                  <div className="sl-item">
                                    <Link to="">
                                      <div className="sl-avatar avatar avatar-sm avatar-circle">
                                        <img
                                          className="img-responsive img-circle"
                                          src="dist/img/user.png"
                                          alt="avatar"
                                        />
                                      </div>
                                      <div className="sl-content">
                                        <p className="inline-block">
                                          <span className="capitalize-font txt-success mr-5 weight-500">
                                            Clay Masse
                                          </span>
                                          <span>
                                            invited to join the meeting in the
                                            conference room at 9.45 am
                                          </span>
                                        </p>
                                        <span className="block txt-grey font-12 capitalize-font">
                                          3 Min
                                        </span>
                                      </div>
                                    </Link>
                                  </div>

                                  <div className="sl-item">
                                    <Link to="">
                                      <div className="sl-avatar avatar avatar-sm avatar-circle">
                                        <img
                                          className="img-responsive img-circle"
                                          src="dist/img/user1.png"
                                          alt="avatar"
                                        />
                                      </div>
                                      <div className="sl-content">
                                        <p className="inline-block">
                                          <span className="capitalize-font txt-success mr-5 weight-500">
                                            Evie Ono
                                          </span>
                                          <span>
                                            added three new photos in the
                                            library
                                          </span>
                                        </p>
                                        <div className="activity-thumbnail">
                                          <img
                                            src="dist/img/thumb-1.jpg"
                                            alt="thumbnail"
                                          />
                                          <img
                                            src="dist/img/thumb-2.jpg"
                                            alt="thumbnail"
                                          />
                                          <img
                                            src="dist/img/thumb-3.jpg"
                                            alt="thumbnail"
                                          />
                                        </div>
                                        <span className="block txt-grey font-12 capitalize-font">
                                          8 Min
                                        </span>
                                      </div>
                                    </Link>
                                  </div>

                                  <div className="sl-item">
                                    <Link to="">
                                      <div className="sl-avatar avatar avatar-sm avatar-circle">
                                        <img
                                          className="img-responsive img-circle"
                                          src="dist/img/user2.png"
                                          alt="avatar"
                                        />
                                      </div>
                                      <div className="sl-content">
                                        <p className="inline-block">
                                          <span className="capitalize-font txt-success mr-5 weight-500">
                                            madalyn rascon
                                          </span>
                                          <span>assigned a new task</span>
                                        </p>
                                        <span className="block txt-grey font-12 capitalize-font">
                                          28 Min
                                        </span>
                                      </div>
                                    </Link>
                                  </div>

                                  <div className="sl-item">
                                    <Link to="">
                                      <div className="sl-avatar avatar avatar-sm avatar-circle">
                                        <img
                                          className="img-responsive img-circle"
                                          src="dist/img/user3.png"
                                          alt="avatar"
                                        />
                                      </div>
                                      <div className="sl-content">
                                        <p className="inline-block">
                                          <span className="capitalize-font txt-success mr-5 weight-500">
                                            Ezequiel Merideth
                                          </span>
                                          <span>
                                            completed project wireframes
                                          </span>
                                        </p>
                                        <span className="block txt-grey font-12 capitalize-font">
                                          yesterday
                                        </span>
                                      </div>
                                    </Link>
                                  </div>

                                  <div className="sl-item">
                                    <Link to="">
                                      <div className="sl-avatar avatar avatar-sm avatar-circle">
                                        <img
                                          className="img-responsive img-circle"
                                          src="dist/img/user4.png"
                                          alt="avatar"
                                        />
                                      </div>
                                      <div className="sl-content">
                                        <p className="inline-block">
                                          <span className="capitalize-font txt-success mr-5 weight-500">
                                            jonnie metoyer
                                          </span>
                                          <span>
                                            created a group 'Hencework' in the
                                            discussion forum
                                          </span>
                                        </p>
                                        <span className="block txt-grey font-12 capitalize-font">
                                          18 feb
                                        </span>
                                      </div>
                                    </Link>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div
                            id="follo_8"
                            className="tab-pane fade"
                            role="tabpanel"
                          >
                            <div className="row">
                              <div className="col-lg-12">
                                <div className="followers-wrap">
                                  <ul className="followers-list-wrap">
                                    <li className="follow-list">
                                      <div className="follo-body">
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Clay Masse
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              No one saves us but ourselves.
                                            </span>
                                          </div>
                                          <button className="btn btn-success pull-right btn-xs fixed-btn">
                                            Follow
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user1.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Evie Ono
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              Unity is strength
                                            </span>
                                          </div>
                                          <button className="btn btn-success btn-outline pull-right btn-xs fixed-btn">
                                            following
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user2.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Madalyn Rascon
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              Respect yourself if you would have
                                              others respect you.
                                            </span>
                                          </div>
                                          <button className="btn btn-success btn-outline pull-right btn-xs fixed-btn">
                                            following
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user3.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Mitsuko Heid
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              I’m thankful.
                                            </span>
                                          </div>
                                          <button className="btn btn-success pull-right btn-xs fixed-btn">
                                            Follow
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Ezequiel Merideth
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              Patience is bitter.
                                            </span>
                                          </div>
                                          <button className="btn btn-success pull-right btn-xs fixed-btn">
                                            Follow
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                        <div className="follo-data">
                                          <img
                                            className="user-img img-circle"
                                            src="dist/img/user1.png"
                                            alt="user"
                                          />
                                          <div className="user-data">
                                            <span className="name block capitalize-font">
                                              Jonnie Metoyer
                                            </span>
                                            <span className="time block truncate txt-grey">
                                              Genius is eternal patience.
                                            </span>
                                          </div>
                                          <button className="btn btn-success btn-outline pull-right btn-xs fixed-btn">
                                            following
                                          </button>
                                          <div className="clearfix"></div>
                                        </div>
                                      </div>
                                    </li>
                                  </ul>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div
                            id="photos_8"
                            className="tab-pane fade"
                            role="tabpanel"
                          >
                            <div className="col-md-12 pb-20">
                              <div className="gallery-wrap">
                                <div className="portfolio-wrap project-gallery">
                                  <ul
                                    id="portfolio_1"
                                    className="portf auto-construct  project-gallery"
                                    data-col="4"
                                  >
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock1.jpg"
                                      data-sub-html="<h6>Bagwati</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock1.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Bagwati
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock2.jpg"
                                      data-sub-html="<h6>Not a Keyboard</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock2.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Not a Keyboard
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock3.jpg"
                                      data-sub-html="<h6>Into the Woods</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock3.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Into the Woods
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock4.jpg"
                                      data-sub-html="<h6>Ultra Saffire</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock4.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          {" "}
                                          Ultra Saffire
                                        </span>
                                      </Link>
                                    </li>

                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock5.jpg"
                                      data-sub-html="<h6>Happy Puppy</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock5.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Happy Puppy
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock6.jpg"
                                      data-sub-html="<h6>Wooden Closet</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock6.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Wooden Closet
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock7.jpg"
                                      data-sub-html="<h6>Happy Puppy</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock7.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Happy Puppy
                                        </span>
                                      </Link>
                                    </li>
                                    <li
                                      className="item"
                                      data-src="dist/img/gallery/equal-size/mock8.jpg"
                                      data-sub-html="<h6>Wooden Closet</h6><p>Classic view from Rigwood Jetty on Coniston Water an old archive shot similar to an old post but a little later on.</p>"
                                    >
                                      <Link to="">
                                        <img
                                          className="img-responsive"
                                          src="dist/img/gallery/equal-size/mock8.jpg"
                                          alt="Image description"
                                        />
                                        <span className="hover-cap">
                                          Wooden Closet
                                        </span>
                                      </Link>
                                    </li>
                                  </ul>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div
                            id="earnings_8"
                            className="tab-pane fade"
                            role="tabpanel"
                          >
                            {/* Row */}
                            <div className="row">
                              <div className="col-lg-12">
                                <form id="example-advanced-form" action="#">
                                  <div className="table-wrap">
                                    <div className="table-responsive">
                                      <table
                                        className="table table-striped display product-overview"
                                        id="datable_1"
                                      >
                                        <thead>
                                          <tr>
                                            <th>Date</th>
                                            <th>Item Sales Colunt</th>
                                            <th>Earnings</th>
                                          </tr>
                                        </thead>
                                        <tfoot>
                                          <tr>
                                            <th colspan="2">total:</th>
                                            <th></th>
                                          </tr>
                                        </tfoot>
                                        <tbody>
                                          <tr>
                                            <td>monday, 12</td>
                                            <td>3</td>
                                            <td>$400</td>
                                          </tr>
                                          <tr>
                                            <td>tuesday, 13</td>
                                            <td>2</td>
                                            <td>$400</td>
                                          </tr>
                                          <tr>
                                            <td>wednesday, 14</td>
                                            <td>3</td>
                                            <td>$420</td>
                                          </tr>
                                          <tr>
                                            <td>thursday, 15</td>
                                            <td>5</td>
                                            <td>$500</td>
                                          </tr>
                                          <tr>
                                            <td>friday, 15</td>
                                            <td>3</td>
                                            <td>$400</td>
                                          </tr>
                                          <tr>
                                            <td>saturday, 16</td>
                                            <td>3</td>
                                            <td>$400</td>
                                          </tr>
                                          <tr>
                                            <td>sunday, 17</td>
                                            <td>3</td>
                                            <td>$400</td>
                                          </tr>
                                          <tr>
                                            <td>monday, 18</td>
                                            <td>3</td>
                                            <td>$500</td>
                                          </tr>
                                          <tr>
                                            <td>tuesday, 19</td>
                                            <td>3</td>
                                            <td>$400</td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                </form>
                              </div>
                            </div>
                          </div>
                          <div
                            id="settings_8"
                            className="tab-pane fade active in"
                            role="tabpanel"
                          >
                            {/* Row */}
                            <div className="row">
                              <div className="col-lg-12">
                                <div className="">
                                  <div className="panel-wrapper collapse in">
                                    <div className="panel-body pa-0">
                                      <div className="col-sm-12 col-xs-12">
                                        <div className="form-wrap">
                                          <form action="#">
                                            <div className="form-body overflow-hide">
                                              <div className="form-group">
                                                <label
                                                  className="control-label mb-10"
                                                  htmlFor="exampleInputuname_01"
                                                >
                                                  First Name
                                                </label>
                                                <div className="input-group">
                                                  <div className="input-group-addon">
                                                    <i className="icon-user"></i>
                                                  </div>
                                                  <div className="form-control">
                                                    {fname}
                                                  </div>
                                                  {/* <input
                                                    type="text"
                                                    className="form-control"
                                                    id="exampleInputuname_01"
                                                    placeholder="willard bryant"
                                                  /> */}
                                                </div>
                                              </div>
                                              <div className="form-group">
                                                <label
                                                  className="control-label mb-10"
                                                  htmlFor="exampleInputuname_01"
                                                  t
                                                >
                                                  Last Name
                                                </label>
                                                <div className="input-group">
                                                  <div className="input-group-addon">
                                                    <i className="icon-user"></i>
                                                  </div>
                                                  <div className="form-control">
                                                    {lname}
                                                  </div>
                                                  {/* <input
                                                    type="text"
                                                    className="form-control"
                                                    id="exampleInputuname_01"
                                                    placeholder="willard bryant"
                                                  /> */}
                                                </div>
                                              </div>
                                              <div className="form-group">
                                                <label
                                                  className="control-label mb-10"
                                                  htmlFor="exampleInputEmail_01"
                                                >
                                                  Email address
                                                </label>
                                                <div className="input-group">
                                                  <div className="input-group-addon">
                                                    <i className="icon-envelope-open"></i>
                                                  </div>
                                                  <div className="form-control">
                                                    {zoho}
                                                  </div>
                                                  {/* <input
                                                    type="email"
                                                    className="form-control"
                                                    id="exampleInputEmail_01"
                                                    placeholder="xyz@gmail.com"
                                                  /> */}
                                                </div>
                                              </div>
                                              <div className="form-group">
                                                <label
                                                  className="control-label mb-10"
                                                  htmlFor="exampleInputContact_01"
                                                >
                                                  Contact number
                                                </label>
                                                <div className="input-group">
                                                  <div className="input-group-addon">
                                                    <i className="icon-phone"></i>
                                                  </div>
                                                  <div className="form-control">
                                                    {contact}
                                                  </div>
                                                  {/* <input
                                                    type="email"
                                                    className="form-control"
                                                    id="exampleInputContact_01"
                                                    placeholder="+102 9388333"
                                                  /> */}
                                                </div>
                                              </div>
                                              <div className="form-group">
                                                <label
                                                  className="control-label mb-10"
                                                  htmlFor="exampleInputpwd_01"
                                                >
                                                  Gender
                                                </label>
                                                <div className="input-group">
                                                  <div className="input-group-addon">
                                                    <i className="icon-lock"></i>
                                                  </div>
                                                  <div className="form-control">
                                                    {gender}
                                                  </div>
                                                  {/* <input
                                                    type="password"
                                                    className="form-control"
                                                    id="exampleInputpwd_01"
                                                    placeholder="Enter pwd"
                                                    value="password"
                                                  /> */}
                                                </div>
                                              </div>
                                            </div>
                                            {/* <div className="form-actions mt-10">
                                              <button
                                                type="submit"
                                                className="btn btn-success mr-10 mb-30"
                                              >
                                                Update profile
                                              </button>
                                            </div> */}
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
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* /Row     */}
          </div>
          {/* Footer  */}
          <footer className="footer container-fluid pl-30 pr-30">
            <div className="row">
              <div className="col-sm-12">
                <p>2017 &copy; Philbert. Pampered by Hencework</p>
              </div>
            </div>
          </footer>
          {/* /Footer  */}
        </div>
        {/* /Main Content */}
      </div>
    </React.Fragment>
  );
}

export default InternPage;
