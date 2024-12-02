import axios from 'axios'
function App() {
  function getOutputUsingPostRequest() {
    axios.post('http://127.0.0.1:8000/api', {
      'text': document.getElementById('txt1').value
    }).then(function (response){
      // console.log(response);
      document.getElementById("result").innerText = response.data["result"];
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
  return (
    <div>
      <div>
        <input type='text' id='txt1' onKeyDown={tryGetCategoryKeyDown}/>
        <input type="button" id='btn1' value='Test' onClick={tryGetCategory} />
        <div id='result'> Result will appear here </div>
      </div>
    </div>
  )
}

export default App
