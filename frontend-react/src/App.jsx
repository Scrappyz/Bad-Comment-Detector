import React from 'react';
import {useState} from 'react';
import axios from 'axios';
import "./App.css";
import Result from "./components/Result.jsx";

function App() {
  function getOutputUsingPostRequest() {
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
  }
  function tryGetCategory() {
    getOutputUsingPostRequest();
  }
  function tryGetCategoryKeyDown(event) {
    if (event.key === "Enter") {
      getOutputUsingPostRequest();
    }
  }

  const [result, setResult] = useState("Empty");
  const [resultColor, setResultColor] = useState();

  return (
    <div className='frame'>
      <div className='form'>
        <div className='header'>
          Bad Comment Detector
        </div>
        <div className='inputs'>
          <div className='input'>
            <input className='bar' placeholder='Enter your comment here' type='text' id='txt1' onKeyDown={tryGetCategoryKeyDown}/>
            <input className='btn' type="button" id='btn1' value='Test' onClick={tryGetCategory} />
          </div>
          <Result text={result} textColor={resultColor} />
          <div className='feedback'>
            <div className='label'>
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
