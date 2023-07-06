   let toastContainer;

    function generateToast({
      message,
      background = '#00214d',
      color = '#fffffe',
      length = '3000ms',
    }){
      toastContainer.insertAdjacentHTML('beforeend', `<p class="toast"
        style="background-color: ${background};
        color: ${color};
        animation-duration: ${length}">
        ${message}
      </p>`)
      const toast = toastContainer.lastElementChild;

      toast.addEventListener('animationend', () => toast.remove())
      toast.classList.add('show');

    }

    (function initToast(){
      document.body.insertAdjacentHTML('afterbegin', `<div class="toast-container"></div>`);
      toastContainer = document.querySelector('.toast-container');
    })();

document.addEventListener('DOMContentLoaded', () => {
        const messages = returnValue;
        console.log(messages);
      messages.forEach((message) => {
        generateToast({
          message: message,
          background: "hsl(45, 100%, 80%)",
          color: "hsl(171 100% 13.1%)",
          length: "5000ms",
        });
      });
    });