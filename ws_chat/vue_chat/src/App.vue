<template>
  <div id="app">
    <div class="container">
      <section ref="chatArea" class="chat-area">
        <p v-for="message in messages" v-bind:key="message.body" class="message"
          :class="{ 'message-out': message.author === 'you', 'message-in': message.author !== 'you' }">
          {{ message.body }}
        </p>
      </section>

      <div class="chat" style="width: 100%; height: 33px;  ">
        <b-form-input id="input" placeholder="Send message.." style="float: left;"
          v-on:keydown.enter="test_keydown_handler" />
        <b-button type="submit" id="send_button" style="float:right" variant="success" v-on:click="send_message">
          Відправити</b-button>
      </div>

    </div>
  </div>
</template>

<script>
import Vue from 'vue'
export default {
  name: 'App',
  components: {
  },
  data() {
    return {
      ws_socket: null,
      reconnecting: false,
      bobMessage: '',
      youMessage: '',
      messages: [
      ]
    }
  },
  methods: {
    sendMessage(direction, mes) {
      console.log('sendMess')
      console.log(direction, mes)
      console.log("Direction: =" + direction + "=")
      console.log(this.messages)
      if (direction === 'out') {
        console.log('OUT')
        this.messages.push({ body: mes, author: 'you' })
      } else if (direction == 'in') {
        console.log('IN')
        //  if (this.messages[this.messages.length - 1] === 'Lost connection.') {
        //   this.messages[this.messages.length - 1] === 'Lost connection..'
        // //   console.log('Lost connection runned') 
        // //   console.log(this.messages)
        // }
        // else
          this.messages.push({ body: mes, author: 'robin' })
          console.log(this.messages)

      } 
      else {
        alert('something went wrong')
      }
      Vue.nextTick(() => {
          console.log('vue next tick') 
          // console.log(this.messages)
          console.log(this.$refs)
          let messageDisplay = this.$refs.chatArea
          messageDisplay.scrollTop = messageDisplay.scrollHeight

      })
    },
    clearAllMessages() {
      this.messages = []
    },
    show_message(message) {
      this.sendMessage('in', message)
    },
    send_message() {
      var input = document.getElementById("input");
      if (input.value === '/reload') {
        console.log('reload');
        this.reconnect()
      }
      else {
        var input_text
        input_text = input.value;
        console.log("send " + input_text)
        this.ws_socket.send(input_text);
        input.value = ""
        this.sendMessage('out', input_text)
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
    reconnect() {
      this.ws_socket = new WebSocket("ws://127.0.0.1:8765");
      this.ws_socket.onmessage = (event) => {
        this.show_message(event.data);
      }
      this.ws_socket.onopen = () => {
        this.show_message('Connected to Robin!');
        this.reconnecting = true;
      };
      this.ws_socket.onclose = () => {
        if (this.reconnecting == true)
          if ((this.messages[this.messages.length - 1] != undefined) && (this.messages[this.messages.length - 1].body == 'Lost connection.')) {
            console.log('lost connection')
          }
          else this.show_message('Lost connection.');
          //this.show_message("'"+this.messages[this.messages.length - 1].body+"'")
        this.reconnecting = true;
        setTimeout(() => { this.reconnect() }, 3000);
        document.getElementById("input").focus();
      };
    },

    toggleDarkMode() {
      console.log('toggleDarkMode');
      if (document.documentElement.classList.contains("light")) {
        document.documentElement.classList.remove("light")
        document.documentElement.classList.add("dark")
      } else if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark")
        document.documentElement.classList.add("light")
      } else {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add("dark")
        } else {
          const hours = new Date().getHours()
          const isDayTime = hours > 6 && hours < 20
          if (isDayTime)
            document.documentElement.classList.add("light")
          else
            document.documentElement.classList.add("dark")
        }
      }
    }
  },
  created() {
    this.toggleDarkMode();
    this.reconnect();
  }
}
</script>

<style>
html {
  font-family: Helvetica;
  box-sizing: border-box;
  /* position: absolute;
  left: 50%;
  transform: translate(-50%, 0); */

}

.message-out {
  color: white;
  margin-left: 48%;
}

.message-in {
  background: #F1F0F0;
  color: black;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin-top: 5px;
  max-width: 600px;
  text-align: center;
}

.container {
  display: block;
  width: 100%;
  height: 95vh !important;
  overflow: hidden;
}

#input {
  width: calc(100% - 113px)
}

.chat-area {
  height: 87%;
  padding: 1em;
  overflow: auto;
  max-width: 580px;
  min-width: 580px;
  margin-top: 10px;
  margin-bottom: 10px;
  /* box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3) */
}

.message {
  width: 45%;
  border-radius: 20px;
  padding: .6em;
  font-size: .95em;
}

.chat-inputs {
  display: flex;
  justify-content: space-between;
}

#person1-input {
  padding: .5em;
}

#person2-input {
  padding: .5em;
}

.form-control:focus {
  border-color: green !important;
  box-shadow: inherit !important;
}

/* COLORS
================================================================================= */
/* automatic/manual light mode */
:root,
:root.light {
  --bg-color: white;
  --border-color: white;
  --my-messages-bg: #407FFF;
  --my-messages-color: white;
  --in-messages-bg: #F0DA62;
  --in-messages-color: black;

}

/* automatic dark mode */
/* ❗️ keep the rules in sync with the manual dark mode below! */



/* manual dark mode 
/* ❗️ keep the rules in sync with the automatic dark mode above! */
:root.dark {
  --bg-color: black;
  --border-color: black;
  --my-messages-bg: #121d0c;
  --in-messages-bg: #2e5d2a;
  --my-messages-color: grey;
  --in-messages-color: black;
}

/* use the variables */
html {
  /* color: #eee; */
  background: var(--bg-color);
}

#app {
  /* color: darkgreen; */
  background: var(--bg-color);
  border: 1px solid var(--border-color);
}

.chat-area {
  background: var(--bg-color);
  /* border: 1px solid var(--border-color); */
}

.container {
  background: var(--bg-color);
}

.message-out {
  background: var(--my-messages-bg);
  color: var(--my-messages-color);
}

.message-in {
  background: var(--in-messages-bg);
  color: var(--in-messages-color);
}

#input::placeholder {
  color: var(--my-messages-color);
  background: var(--my-messages-bg);
  /* border: 1px solid var(--border-color); */
}

#input {
  background: var(--my-messages-bg);
  /* border: 1px solid var(--border-color); */

  color: var(--my-messages-color);
}

#send_button {
  background: var(--my-messages-bg);
  color: var(--my-messages-color);
}

body {
  color: var(--some-value);
  background-color: var(--bg-color);
}
</style>
