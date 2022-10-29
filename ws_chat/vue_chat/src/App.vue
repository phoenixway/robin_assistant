<template>
  <div id="app">
    <div class="container">
      <div class="messages">
        <b-form-textarea id="output"></b-form-textarea>
      </div>
      <div class="chat" style="width: 100%; height: 33px;  ">
        <b-form-input id="input" placeholder="Send message.." style="float: left;"
          v-on:keydown.enter="test_keydown_handler" />
        <b-button type="submit" id="send_button" style="float:right" variant="primary" v-on:click="send_message">
          Відправити</b-button>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  components: {
  },
  data() {
    return {
      ws_socket: null,
      reconnecting: false,
    }
  },
  methods: {
    show_message(message) {
      let output = document.getElementById("output");  
      if (output.value != "")
        output.value = output.value + "\r\n" + message;
      else
        output.value = message;
    },
    send_message() {
      var input = document.getElementById("input");
      if (input.value === '/reload') {
        console.log('reload');
        this.ws_socket.close();
        this.ws_socket = new WebSocket("ws://127.0.0.1:8765");
      }
      else {
        var input_text
        input_text = input.value;
        console.log("send " + input_text)
        this.ws_socket.send(input_text);
        input.value = ""
      }

    },
    test_keydown_handler(e) {
      console.log("enter")
      if (e.which === 13) {
        this.send_message()
        e.preventDefault()
        // document.getElementById("input").focus();
      }
    },
    reconnect(){
      this.ws_socket = new WebSocket("ws://127.0.0.1:8765");
      this.ws_socket.onmessage = (event) => {
        this.show_message(event.data);
      }
      this.ws_socket.onopen = () => {
        this.show_message('Connected to server!');
        this.reconnecting = true;
      };
      this.ws_socket.onclose = () => {
        if (this.reconnecting == true)
          this.show_message('Lost connection.');
        this.reconnecting = true;
        setTimeout(() => {this.reconnect()}, 3000);
      };
    },
  },
  created() {
    this.reconnect();
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
  margin-top: 5px;
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
