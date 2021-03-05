import React, { useState, useEffect } from "react";
import Preloader from "./components/Dashboard/Common/Preloader";
import Pusher from "pusher-js";
import Axios from "axios";
// Router
import { BrowserRouter as Router } from "react-router-dom";
import AppRouter from "./routers/AppRouter";
import UserContext from "./context/UserContext";
import "./App.css";

function App() {
  const [userData, setUserData] = useState({
    token: undefined,
    user: undefined,
  });
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    Axios.get("/api/messages/sync").then((response) => {
      setMessages(response.data);
    });
  }, []);

  useEffect(() => {
    const pusher = new Pusher("9b4bb56b8cb856641dae", {
      cluster: "ap2",
    });

    const channel = pusher.subscribe("message");
    channel.bind("inserted", (newMessage) => {
      setMessages([...messages, newMessage]);
    });

    return () => {
      channel.unbind_all();
      channel.unsubscribe();
    };
  }, [messages]);

  console.log(messages);

  useEffect(() => {
    const checkLoggedIn = async () => {
      let token = localStorage.getItem("auth-token");
      if (token === null) {
        localStorage.setItem("auth-token", "");
        token = "";
      }

      const tokenRes = await Axios.post("/api/users/tokenIsValid", null, {
        headers: { "x-auth-token": token },
      });
      if (tokenRes.data) {
        const userRes = await Axios.get("/api/auth/", {
          headers: { "x-auth-token": token },
        });
        setUserData({
          token,
          user: userRes.data,
        });
      }
    };

    checkLoggedIn();
  }, []);

  return (
    <div className="App">
      <Preloader />
      <UserContext.Provider value={{ userData, setUserData }}>
        <Router forceRefresh>
          <AppRouter messages={messages} />
        </Router>
      </UserContext.Provider>
    </div>
  );
}

export default App;
