function getMessages(url, container) {
  fetch(url)
    .then(response => {
      console.log("Response received!", response);
      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }
      return response.json();
    })
    .then(messages => {
      console.log(messages);
      messages.sort((a, b) => new Date(b.date) - new Date(a.date));
      messages.reverse();

      let messagesHTML = "";
      let chatContainer = "<div class='chat-container'>";
      let chatTitle = `<h2 class='chat-title'>SALA DINÁMICA</h2>`;
      chatContainer += chatTitle;

      messages.forEach(message => {
        let messageHTML = "<div class='chat-message'>";

        let messageCreator = `<span class='message-creator'>${message.author}</span>`;
        messageHTML += messageCreator;
        messageHTML += ": ";

        if (message.isimg) {
          let img = `<img src='${message.text}' alt='Imagen'>`;
          messageHTML += img;
        } else {
          messageHTML += message.text;
        }

        let messageDate = `<span class='message-date'>${message.date}</span>`;
        messageHTML += messageDate;

        messageHTML += "</div>";

        messagesHTML += messageHTML;
      });

      chatContainer += messagesHTML;
      chatContainer += "</div>";

      container.innerHTML = chatContainer;
    })
    .catch(error => {
      console.log("Error decoding JSON:", error);
    });
}


window.addEventListener("DOMContentLoaded", event => {
  console.log("DOM fully loaded and parsed");
  const container = document.querySelector("#messages");
  getMessages(url_messages, container);
  setInterval(() => {
    console.log("Interval");
    getMessages(url_messages, container);
  }, 2*1000); //
});


