<template>
  <div id="app">
    <div class="container">
      <div class="messages"><b-form-textarea id="output"></b-form-textarea></div>
      <div class="chat" style="width: 100%; height: 33px;  ">
          <b-form-input  id="input" placeholder="Send message.." style="float: left;" v-on:keydown.enter="test_keydown_handler"/>
          <b-button type="submit" id="send_button" style="float:right" variant="primary" v-on:click="send_message">Відправити</b-button>
      </div>

    </div>
  </div>
</template>

<script>

var mySocket = new WebSocket("ws://127.0.0.1:8765");

window.addEventListener("load", function () {
  document.getElementById("input").focus();
});

export default {
  name: 'App',
  metaInfo: {
      // if no subcomponents specify a metaInfo.title, this title will be used
      title: 'Default Title',
      // all titles will be injected into this template
      titleTemplate: '%s | My Awesome Webapp'
    },
  components: {

  },
  data() {
      return {
        ws_socket: mySocket
      }
    },
  methods: {
    send_message(){
      var input = document.getElementById("input");
      var input_text
      input_text = input.value;
      console.log("send " + input_text)
      this.ws_socket.send(input_text);
      input.value = ""
    },
  test_keydown_handler(e) {
    console.log("enter")
     if (e.which === 13) {
      this.send_message()
      e.preventDefault()
      // document.getElementById("input").focus();
     }
  },
  
  },
  created(){
    this.ws_socket.onmessage = function (event) {
    var output = document.getElementById("output");
    console.log("rec: " + event.data)
    // put text into our output div
    if (output.value != "")
      output.value = output.value + "\r\n" + event.data;
    else
      output.value = event.data;
  }
}
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  margin-top: 15px;
}

#output {
  width: 100%;
  height: 100%;
  -webkit-box-sizing: border-box;
  /* Safari/Chrome, other WebKit */
  -moz-box-sizing: border-box;
  /* Firefox, other Gecko */
  box-sizing: border-box;
  /* Opera/IE 8+ */
}

.container {
  display: block;
  width: 100%;
  height: 95vh !important;
  overflow: hidden;
}

.messages {
  float: left;
  width: 100%;
  height: 90%;
  display: block;
  overflow: scroll;
  margin-bottom: 10px;
}

#input {
  width: calc(100% - 113px)
}
</style>
