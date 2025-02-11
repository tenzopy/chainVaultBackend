document.addEventListener("DOMContentLoaded", function () {

  // Handle click event on the upload button in the left panel
  document.getElementById('uploadBtnLeft').addEventListener('click', function () {
    document.getElementById('uploadModal').style.display = 'block';
  });

  // Handle click event on the share button in the left panel
  document.getElementById('shareBtnLeft').addEventListener('click', function () {
    document.getElementById('shareModal').style.display = 'block';
  });

  // Handle click event on the upload button in the top right corner
  document.getElementById('uploadBtnRight').addEventListener('click', function () {
    document.getElementById('uploadModal').style.display = 'block';
  });

  // Function to handle file upload
  function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const passwordInput = document.getElementById('passwordInput');
    const file = fileInput.files[0];
    const password = passwordInput.value;
    const fileName = file.name;

    // Check if a file is selected
    if (!file) {
      alert("Please select a file.");
      return;
    }

    // Check if a password is provided
    var lowerUpperNumberSpclLetters = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/;
    if (passwordInput.value.match(lowerUpperNumberSpclLetters)) {
      passwordInput.setCustomValidity("");
    } else {
      passwordInput.setCustomValidity("Password should contain 8-15 characters and lowerCase,upperCase,numericals & special characters.");
      passwordInput.reportValidity();
      passwordInput.addEventListener("input", function () {
        passwordInput.setCustomValidity("");
      })
      return;
    }

    // Perform file upload here

    var csrftoken = getCookie('csrftoken');
    const formData = new FormData;

    formData.append('uploadFile', file)
    formData.append('password', password)

    const options = {
      credentials: 'include',
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    };
    fetch(`/dashboard/upload/`, options)
      .then((response) => response.json())
      .then((response) => {
        if (response.status == 'ok') {
          var msg = document.getElementById('msg');
          msg.innerHTML = "File Uploaded !";
          msg.style.color = "green";
          msg.style.display = "block";

          var existingDiv = document.getElementById('fileList');

          var newDiv = document.createElement('div');
          newDiv.className = 'fileItem';
          newDiv.id = fileName;
          newDiv.innerHTML = '<p>' + fileName + '</p>' +
            '<div>' +
            '<button class="download-btn" data-filename="' + fileName + '" data-filesize="' + response.file_size + '" data-filecreated="' + response.file_created + '" data-filetype="' + response.file_type + '" data-shared="False" onclick="fileInfo(this)">Info</button>&nbsp;&nbsp;' +
            '<button class="download-btn" data-filename="' + fileName + '" data-shared="False" onclick="Downloadz(this)">Download</button>&nbsp;&nbsp;' +
            '<button class="delete-btn" data-filename="' + fileName + '" onclick="deleteFile(this)">Delete</button>' +
            '</div>';

          existingDiv.appendChild(newDiv);

          var selectElement = document.getElementById('file-select');
          var newOption = document.createElement('option');
          newOption.value = fileName;
          newOption.textContent = fileName;
          selectElement.appendChild(newOption);

        }
      });

    // Clear input fields after upload
    var msg = document.getElementById('msg');
    msg.innerHTML = "File is being Uploaded...";
    msg.style.color = "green";
    msg.style.display = "block";
    fileInput.value = '';
    passwordInput.value = '';
    // Close the upload modal after upload
    //document.getElementById('uploadModal').style.display = 'none';
  }

  // Handle click event on the upload button in the modal
  document.getElementById('uploadSubmitBtn').addEventListener('click', handleFileUpload);

  // Handle click event on the upload button in the modal
  document.getElementById('shareSubmitBtn').addEventListener('click', handleShare);

  // Handle click event on the submit button in the password modal
  document.getElementById('passwordSubmitBtn').addEventListener('click', function () {
    const filename = document.getElementById('passwordModal').getAttribute('data-filename');
    const passwordVerifier = document.getElementById('filePassword')
    const password = passwordVerifier.value;
    // Perform your password validation here
    // For demonstration, simply log the filename and password

    var lowerUpperNumberSpclLetters = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/;
    if (passwordVerifier.value.match(lowerUpperNumberSpclLetters)) {
      passwordVerifier.setCustomValidity("");
    } else {
      passwordVerifier.setCustomValidity("Password should contain 8-15 characters and lowerCase,upperCase,numericals & special characters.");
      passwordVerifier.reportValidity();
      passwordVerifier.addEventListener("input", function () {
        passwordVerifier.setCustomValidity("");
      })
      return;
    }


    // Perform file upload here

    var csrftoken = getCookie('csrftoken');
    const formData = new FormData;

    formData.append('file_name', filename)
    formData.append('password', password)

    const options = {
      credentials: 'include',
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    };
    fetch(`/dashboard/download/`, options)
      .then((response) => response.json())
      .then((response) => {
        if (response.status == 'ok') {
          document.getElementById('msg1').innerHTML = '';
          var a = document.createElement('a');
          a.setAttribute('href', response.download_url);
          a.download = filename;
          a.id = 'downButton';
          a.textContent = 'Click Me';
          const baseDiv = document.getElementById('downPass')
          baseDiv.appendChild(a)
        }
        else {
          document.getElementById('msg1').innerHTML = '';
          var b = document.createElement('h4');
          b.innerHTML = response.status;
          b.style.color = 'red';
          const baseDiv = document.getElementById('downPass')
          baseDiv.appendChild(b)


        }
      });

    var msg = document.getElementById('msg1');
    msg.innerHTML = "Fetching Data..";
    msg.style.color = "green";
    msg.style.display = "block";
    document.getElementById('filePassword').value = '';
    // Close the password modal after processing
    //document.getElementById('passwordModal').style.display = 'none';
  });

  // Close the modal when the close button is clicked
  document.querySelectorAll('.close').forEach(function (closeBtn) {
    closeBtn.addEventListener('click', function () {
      this.closest('.modal').style.display = 'none';
      document.getElementById('downPass').innerHTML = '';
      document.getElementById('msg').innerHTML = '';
      document.getElementById('msg1').innerHTML = '';
      document.getElementById('msgShare').innerHTML = '';
    });
  });
});

function handleShare() {
  const fileInput = document.getElementById('fileInputShare');
  const fileSelection = document.getElementById('file-select');
  const passwordInput = document.getElementById('passwordShareInput');
  const receiverInput = document.getElementById('receiver');
  const file = fileInput.files[0];
  const password = passwordInput.value;
  const receiver = receiverInput.value;


  // Check if a password is provided
  var lowerUpperNumberSpclLetters = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/;
  if (passwordInput.value.match(lowerUpperNumberSpclLetters)) {
    passwordInput.setCustomValidity("");
  } else {
    passwordInput.setCustomValidity("Password should contain 8-15 characters and lowerCase,upperCase,numericals & special characters.");
    passwordInput.reportValidity();
    passwordInput.addEventListener("input", function () {
      passwordInput.setCustomValidity("");
    })
    return;
  }

  // Perform file upload here

  var csrftoken = getCookie('csrftoken');
  const formData = new FormData;

  if (!file) {
    formData.append('file_name', fileSelection.value);
  }
  else {
    formData.append('uploadFile', file);
  }

  formData.append('receiver', receiver);
  formData.append('password', password);

  const options = {
    credentials: 'include',
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formData
  };
  const fileselectionValue = fileSelection.value;
  fetch(`/dashboard/share/`, options)
    .then((response) => response.json())
    .then((response) => {
      if (response.status == 'ok') {
        var msg = document.getElementById('msgShare');
        msg.innerHTML = "File Shared !";
        msg.style.color = "green";
        msg.style.display = "block";

        if (!file) {
          SelectedFileDiv = document.getElementById(fileselectionValue);
          SelectedFileDiv.remove();

          var existingDiv = document.getElementById('fileList');

          var newDiv = document.createElement('div');
          newDiv.className = 'fileItem';
          newDiv.id = fileselectionValue;
          newDiv.innerHTML = '<p>' + fileselectionValue + '&emsp;(SHARED)</p>' +
            '<div>' +
            '<button class="download-btn" data-filename="' + fileselectionValue + '" data-filesize="' + response.file_size + '" data-filecreated="' + response.file_created + '" data-filetype="' + response.file_type + '" data-shared="True" data-sender="none" data-receiver="' + receiver + '" onclick="fileInfo(this)">Info</button>&nbsp;&nbsp;' +
            '<button class="download-btn" data-filename="' + fileselectionValue + '" data-shared="True" data-sender="none" data-receiver="' + receiver + '" onclick="Downloadz(this)">Download</button>&nbsp;&nbsp;' +
            '<button class="delete-btn" data-filename="' + fileselectionValue + '" onclick="deleteFile(this)">Delete</button>' +
            '</div>';

          existingDiv.appendChild(newDiv);
        }
        else {
          var existingDiv = document.getElementById('fileList');

          var newDiv = document.createElement('div');
          newDiv.className = 'fileItem';
          newDiv.id = file.name;
          newDiv.innerHTML = '<p>' + file.name + '&emsp;(SHARED)</p>' +
            '<div>' +
            '<button class="download-btn" data-filename="' + file.name + '" data-filesize="' + response.file_size + '" data-filecreated="' + response.file_created + '" data-filetype="' + response.file_type + '" data-shared="True" data-sender="none" data-receiver="' + receiver + '" onclick="fileInfo(this)">Info</button>&nbsp;&nbsp;' +
            '<button class="download-btn" data-filename="' + file.name + '" data-shared="True" data-sender="none" data-receiver="' + receiver + '" onclick="Downloadz(this)">Download</button>&nbsp;&nbsp;' +
            '<button class="delete-btn" data-filename="' + file.name + '" onclick="deleteFile(this)">Delete</button>' +
            '</div>';

          existingDiv.appendChild(newDiv);
        }

      }
    });

  var msg = document.getElementById('msgShare');
  msg.innerHTML = "Sharing Your File";
  msg.style.color = "green";
  msg.style.display = "block";
  fileInput.value = '';
  passwordInput.value = '';
  fileSelection.value = '';
  receiverInput.value = '';

}


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

function logout() {
  window.location.href = '/account/logout/';
}

function toggleUpload() {
  var fileSelect = document.getElementById('file-select');
  var uploadFile = document.getElementById('fileInputShare');
  var selectedFile = fileSelect.value;

  if (selectedFile !== '') {
    uploadFile.disabled = true;
  } else {
    uploadFile.disabled = false;
  }
}

function toggleSelect() {
  var fileSelect = document.getElementById('file-select');
  var uploadFile = document.getElementById('fileInputShare');
  var uploadedFile = uploadFile.files[0].name;

  if (uploadedFile !== '') {
    fileSelect.disabled = true;
  } else {
    fileSelect.disabled = false;
  }
}

function deleteFile(button) {
  const filename = button.dataset.filename;
  var csrftoken = getCookie('csrftoken');
  const formData = new FormData;

  formData.append('file_name', filename);

  const options = {
    credentials: 'include',
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formData
  };
  fetch(`/dashboard/delete/`, options)
    .then((response) => response.json())
    .then((response) => {
      if (response.status == 'ok') {
        var delItem = button.parentElement.parentElement;
        delItem.remove();
      }
    });

  // alert("Delete Initated")

}



// Function to handle file item click
function handleFileItemClick(filename, shared, sender, receiver) {
  document.getElementById('passwordModal').style.display = 'block';
  // Pass filename to the password modal for reference
  document.getElementById('passwordModal').setAttribute('data-filename', filename);
  if (shared == "False") {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename;
  }
  else if (sender == 'none') {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename + "<br>Sent to : " + receiver;
  }
  else {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename + "<br>Received From : " + sender;
  }

}
function Downloadz(buttonz) {
  const filename = buttonz.dataset.filename;
  const sender = buttonz.dataset.sender;
  const receiver = buttonz.dataset.receiver;
  const shared = buttonz.dataset.shared;
  handleFileItemClick(filename, shared, sender, receiver);
}

function fileInfoClick(filename, shared, sender, receiver, filesize, filetype, filecreated) {
  document.getElementById('infoModal').style.display = 'block';
  // Pass filename to the password modal for reference
  document.getElementById('infoModal').setAttribute('data-filename', filename);
  if (shared == "False") {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename + "<br><br>File Size : " + filesize + "<br><br>FileType : " + filetype + "<br><br>Created On : " + filecreated;
  }
  else if (sender == 'none') {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename + "<br><br>Sent to : " + receiver + "<br><br>File Size : " + filesize + "<br><br>FileType : " + filetype + "<br><br>Created On : " + filecreated;
  }
  else {
    document.getElementById('msgfile').innerHTML = "Filename : " + filename + "<br><br>Received From : " + sender + "<br><br>File Size : " + filesize + "<br><br>FileType : " + filetype + "<br><br>Created On : " + filecreated;
  }

}
function fileInfo(buttonz) {
  const filename = buttonz.dataset.filename;
  const sender = buttonz.dataset.sender;
  const receiver = buttonz.dataset.receiver;
  const shared = buttonz.dataset.shared;
  const filesize = formatBytes(buttonz.dataset.filesize);
  const filetype = buttonz.dataset.filetype;
  const filecreated = parseInt(buttonz.dataset.filecreated);
  const file_created = new Date(filecreated);
  fileInfoClick(filename, shared, sender, receiver, filesize, filetype, file_created);
}

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function fetchData() {
  var csrftoken = getCookie('csrftoken');
  const options = {
    credentials: 'include',
    method: 'GET',
    headers: {
      'X-CSRFToken': csrftoken
    },
  };
  fetch(`/hashtable/fetch_data`, options)
    .then((response) => response.json())
    .then((response) => {
      if (response.status == 'ok') {
        document.getElementById('fetchBtnRight').innerHTML = "Fetched Data";
        location.reload();
      }
      document.getElementById('fetchBtnRight').innerHTML = "Fetching..";
      document.getElementById('fetchBtnRight').disabled = true;
    });

}