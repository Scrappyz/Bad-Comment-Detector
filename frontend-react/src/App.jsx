import React from 'react';
import {useState, useEffect} from 'react';
import axios from 'axios';
import "./App.css";
import Result from "./components/Result.jsx";

function App() {
  function heartBeat() {
    axios.get("https://bad-comment-detector-server.onrender.com/").then(function() {
      // alert("Connected!");
      setConnection(true);
    }).catch(function() {
      setConnection(false);
    });
  }

  useEffect(function(){
    setInterval(heartBeat, 5000);
    if (localStorage.getItem("limit") === null) {
      localStorage.setItem("limit", "100");
      let nextTime = (new Date()).getTime();
      nextTime = nextTime + 60 * 60 * 1000;
      localStorage.setItem("nextTime", nextTime.toString());
    }
  }, []);

  function getOutputUsingPostRequest() {
    var limit = parseInt(localStorage.getItem("limit"));
    var nextTime = parseInt(localStorage.getItem("nextTime"));
    var currentTime = (new Date()).getTime();
    if (limit < 1 && currentTime < nextTime) {
      alert("Limit exceeded");
      return ;
    }
    if (currentTime >= nextTime) {
      limit = 5;
      localStorage.setItem("limit", "100");
      nextTime = (new Date()).getTime();
      nextTime = nextTime + 60 * 60 * 1000;
      localStorage.setItem("nextTime", nextTime.toString());
    }

    axios.post('https://bad-comment-detector-server.onrender.com/api', {
      'text': document.getElementById('txt1').value
    }).then(function (response){
      // console.log(response);
      // document.getElementById("result").innerText = response.data["result"];
      let result = response.data["result"];
      if(result === "toxic") {
        setResult("Toxic");
        setResultColor("red");
      } else {
        setResult("Clean");
        setResultColor("green");
      }
    });

    limit = limit - 1;
    localStorage.setItem("limit", limit.toString());

  }

  function tryGetCategory() {
    getOutputUsingPostRequest();
  }

  function tryGetCategoryKeyDown(event) {
    if (event.key === "Enter") {
      getOutputUsingPostRequest();
    }
  }

  const [connection, setConnection] = useState(false);
  const [result, setResult] = useState("Empty");
  const [resultColor, setResultColor] = useState();

  return (
    <div className='frame'>
      <div className='form'>
        <div className='header'>
          Bad Comment Detector
        </div>
        <div className='content'>
          <div className='status-group' >
            <div className='label-box'>
              Status
            </div>
            {connection ? <img className='status' src='../public/check.svg' style={{backgroundColor: "rgb(0, 234, 0)"}} /> : <img className='status' src='../public/cross.svg' style={{backgroundColor: "red"}} />}
          </div>
          <div className='input-group'>
            <input className='input' placeholder='Enter your comment here' type='text' id='txt1' onKeyDown={tryGetCategoryKeyDown}/>
            <input className='btn' type="button" id='btn1' value='Test' onClick={tryGetCategory} />
          </div>
          <Result text={result} textColor={resultColor} />
          <div className='feedback-group'>
            <div className='label-box'>
              Expected
            </div>
            <button className='btn'>Result</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
