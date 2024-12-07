import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "./App.css";
import Result from "./components/Result.jsx";

function App() {
  const [connection, setConnection] = useState(false);
  const [result, setResult] = useState("Empty");
  const [resultColor, setResultColor] = useState();
  const [dropdown, setDropdown] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [expectedResult, setExpectedResult] = useState("Result");

  function heartBeat() {
    axios.get("https://bad-comment-detector-server.onrender.com/")
      .then(() => setConnection(true))
      .catch(() => setConnection(false));
  }

  useEffect(() => {
    const interval = setInterval(heartBeat, 5000);
    if (!localStorage.getItem("limit")) {
      localStorage.setItem("limit", "100");
      const nextTime = Date.now() + 60 * 60 * 1000;
      localStorage.setItem("nextTime", nextTime.toString());
    }
    return () => clearInterval(interval);
  }, []);

  function getOutputUsingPostRequest() {
    const limit = parseInt(localStorage.getItem("limit"));
    const nextTime = parseInt(localStorage.getItem("nextTime"));
    const currentTime = Date.now();

    // Check if limit is depleted
    if (limit < 1 && currentTime < nextTime) {
      alert("Limit exceeded");
      return;
    }

    // Time and limit resets
    if (currentTime >= nextTime) {
      localStorage.setItem("limit", "100");
      const newNextTime = Date.now() + 60 * 60 * 1000;
      localStorage.setItem("nextTime", newNextTime.toString());
    }

    axios.post('https://bad-comment-detector-server.onrender.com/api', { text: inputValue })
      .then((response) => {
        const result = response.data.result;
        setResult(result === "toxic" ? "Toxic" : "Clean");
        setResultColor(result === "toxic" ? "red" : "green");
      });

    // Decrement limit
    // localStorage.setItem("limit", (limit - 1).toString());
  }

  function tryGetCategory() {
    getOutputUsingPostRequest();
  }

  function tryGetCategoryKeyDown(event) {
    if (event.key === "Enter") {
      getOutputUsingPostRequest();
    }
  }

  const toggleDropdown = () => setDropdown((prevState) => !prevState);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (!event.target.closest('.dropdown')) {
        setDropdown(false);
      }
    };
    document.addEventListener('click', handleOutsideClick);

    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, []);

  const selectExpectedResult = (result) => {
    setExpectedResult(result);
    setDropdown(false);
  }

  return (
    <div className="frame">
      <div className="form">
        <div className="header">Bad Comment Detector</div>
        <div className="content">
          <div className="status-group">
            <div className="label-box">Status</div>
            {connection ? (
              <img className="status" src="../public/check.svg" style={{ backgroundColor: "rgb(0, 234, 0)" }} />
            ) : (
              <img className="status" src="../public/cross.svg" style={{ backgroundColor: "red" }} />
            )}
          </div>
          <div className="input-group">
            <input
              className="input"
              placeholder="Enter your comment here"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={tryGetCategoryKeyDown}
            />
            <input className="btn" type="button" id="btn1" value="Test" onClick={tryGetCategory} />
          </div>
          <Result text={result} textColor={resultColor} />
          <div className="feedback-group">
            <div className="expected-group">
              <div className="label-box">Expected</div>
              <div className="dropdown">
                <button onClick={toggleDropdown} className="btn">{expectedResult}</button>
                {dropdown && (
                  <div className="dropdown-items">
                    <button onClick={() => selectExpectedResult("Clean")} className="items">Clean</button>
                    <button onClick={() => selectExpectedResult("Toxic")} className="items">Toxic</button>
                  </div>
                )}
              </div>
            </div>
            <button className="send-btn">Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
