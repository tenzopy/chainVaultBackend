document.addEventListener("DOMContentLoaded", function() {
    const fileItems = document.querySelectorAll('.fileItem');
  
    // Function to handle file item click
    function handleFileItemClick(filename) {
      document.getElementById('passwordModal').style.display = 'block';
      // Pass filename to the password modal for reference
      document.getElementById('passwordModal').setAttribute('data-filename', filename);
    }
  
    // Add click event listener to file items
    fileItems.forEach(function(fileItem) {
      fileItem.addEventListener('click', function() {
        const filename = this.dataset.filename;
        handleFileItemClick(filename);
      });
    });
  
    // Handle click event on the upload button in the left panel
    document.getElementById('uploadBtnLeft').addEventListener('click', function() {
      document.getElementById('uploadModal').style.display = 'block';
    });
  
    // Handle click event on the upload button in the top right corner
    document.getElementById('uploadBtnRight').addEventListener('click', function() {
      document.getElementById('uploadModal').style.display = 'block';
    });
  
    // Function to handle file upload
    function handleFileUpload() {
      const fileInput = document.getElementById('fileInput');
      const passwordInput = document.getElementById('passwordInput');
      const file = fileInput.files[0];
      const password = passwordInput.value;
  
      // Check if a file is selected
      if (!file) {
        alert("Please select a file.");
        return;
      }
  
      // Check if a password is provided
      if (!password) {
        alert("Please enter a password.");
        return;
      }
  
      // Perform file upload here

      var csrftoken = getCookie('csrftoken');
    const formData = new FormData;

    formData.append('uploadFile',file)
    formData.append('password',password)

    const options = {
        credentials: 'include',
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken
        },
        body: formData  
    };
    fetch(`/dashboard/upload/`,options)
      .then((response) => response.json())
      .then((response) => { 
        if (response.status == 'ok') {
            const msg = document.getElementById('msg');
            msg.innerHTML = "File Uploaded !";
            msg.style.color = "green";
            msg.style.display = "block";

        }
      });
  
      // Clear input fields after upload
      fileInput.value = '';
      passwordInput.value = '';
      // Close the upload modal after upload
      //document.getElementById('uploadModal').style.display = 'none';
    }
  
    // Handle click event on the upload button in the modal
    document.getElementById('uploadSubmitBtn').addEventListener('click', handleFileUpload);
  
    // Handle click event on the submit button in the password modal
    document.getElementById('passwordSubmitBtn').addEventListener('click', function() {
      const filename = document.getElementById('passwordModal').getAttribute('data-filename');
      const password = document.getElementById('filePassword').value;
  
      // Perform your password validation here
      // For demonstration, simply log the filename and password

      if (!password) {
        alert("Please enter a password.");
        return;
      }
  
      // Perform file upload here

      var csrftoken = getCookie('csrftoken');
    const formData = new FormData;

    formData.append('file_name',filename)
    formData.append('password',password)

    const options = {
        credentials: 'include',
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken
        },
        body: formData  
    };
    fetch(`/dashboard/download/`,options)
      .then((response) => response.json())
      .then((response) => { 
        if (response.status == 'ok') {
            var a = document.createElement('a');
            a.setAttribute('href', response.download_url);   
            a.download = filename;
            a.id = 'downButton';
            a.textContent = 'Click Me';
            const baseDiv = document.getElementById('downPass')
            baseDiv.appendChild(a)
            document.getElementById('filePassword').value = '';


        }
      });
  
      // Close the password modal after processing
      //document.getElementById('passwordModal').style.display = 'none';
    });
  
    // Close the modal when the close button is clicked
    document.querySelectorAll('.close').forEach(function(closeBtn) {
      closeBtn.addEventListener('click', function() {
        this.closest('.modal').style.display = 'none';
        document.getElementById('downPass').style.display = 'none';
        document.getElementById('msg').style.display = 'none';
      });
    });
  });
  

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }