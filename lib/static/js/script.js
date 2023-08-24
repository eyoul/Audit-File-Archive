var treeLinks = document.querySelectorAll('.tree-menu a');
for (var i = 0; i < treeLinks.length; i++) {
  treeLinks[i].addEventListener('click', function(event) {
    var li = this.parentNode;
    if (li.classList.contains('active')) {
      li.classList.remove('active');
    } else {
      var siblings = li.parentNode.children;
      for (var j = 0; j < siblings.length; j++) {
        if (siblings[j] !== li) {
          siblings[j].classList.remove('active');
        }
      }
      li.classList.add('active');
    }
  });
}

var links = document.querySelectorAll('.tree-menu a[data-file]');
for (var i = 0; i < links.length; i++) {
  links[i].addEventListener('click', function(event) {
    event.preventDefault();
    renderFile(this.getAttribute('data-file'), this.getAttribute('data-type'));
  });
}
function renderFile(filePath) {
  console.log('renderFile called with filePath', filePath);
  var fileContainer = document.getElementById('pdf');
  fileContainer.innerHTML = '';
  var fileType = filePath.split('.').pop().toLowerCase();
  if (fileType == 'pdf') {
    // Render PDF file
    var object = document.createElement('object');
    object.data = filePath;
    object.type = 'application/pdf';
    object.width = '75%';
    object.height = '700px';
    fileContainer.appendChild(object);
  } else if (fileType == 'doc' || fileType == 'docx') {
    // Render Word file as a downloadable link
    var link = document.createElement('a');
    link.href = filePath;
    link.download = true;
    link.appendChild(document.createTextNode('Download file'));
    fileContainer.appendChild(link);
  } else if (fileType == 'jpg' || fileType == 'jpeg' || fileType == 'png') {
    // Render image file
    var img = document.createElement('img');
    img.src = filePath;
    fileContainer.appendChild(img);
  } else {
    // Unknown file type
    fileContainer.innerHTML = 'Cannot display this file type. Please download the file to view it: <a href="' + filePath + '">Download file</a>';
  }
}
cd 
var pdfLinks = document.querySelectorAll('a[data-type="pdf"]');
pdfLinks.forEach(function(link) {
  link.addEventListener('click', function(event) {
    event.preventDefault();
    var filePath = link.getAttribute('data-file');
    renderFile(filePath);
  });
});

function displaySearchResults(results) {
  var list = document.querySelector('#document-list');
  list.innerHTML = '';
  results.forEach(function(result) {
    var link = document.createElement('a');
    link.href = '#';
    link.dataset.file = result.file_path;
    link.dataset.type = result.file_type;
    link.textContent = result.name;
    link.addEventListener('click', function(event) {
      event.preventDefault();
      var file = this.dataset.file;
      var type = this.dataset.type;
      var pdf = document.querySelector('#pdf');
      if (!file || !type || !pdf) {
        console.error('File or type not specified.');
        return;
      }
      pdf.setAttribute('data', file);
      pdf.setAttribute('type', type);
      console.log('File set to:', file);
    });
    var listItem = document.createElement('li');
    listItem.appendChild(link);
    list.appendChild(listItem);
  });
}