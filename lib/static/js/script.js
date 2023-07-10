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

function renderFile(filePath, fileType) {
  console.log('renderFile called with filePath', filePath, 'and fileType', fileType);
  var fileContainer = document.getElementById('pdf');
  
  // Remove any existing elements from the fileContainer section
  fileContainer.innerHTML = '';
  
  if (fileType == 'pdf') {
    console.log('rendering PDF file');
    var object = document.createElement('object');
    object.data = filePath;
    object.type = 'application/pdf';
    object.width = '100%';
    object.height = '600px';
    fileContainer.appendChild(object);
  } else if (fileType == 'doc' || fileType == 'docx') {
    console.log('rendering Word file');
    var iframe = document.createElement('iframe');
    iframe.src = "https://view.officeapps.live.com/op/embed.aspx?src=" + encodeURIComponent(filePath);
    fileContainer.appendChild(iframe);
  } else if (fileType == 'jpg' || fileType == 'jpeg' || fileType == 'png') {
    console.log('rendering image file');
    var img = document.createElement('img');
    img.src = filePath;
    fileContainer.appendChild(img);
  } else {
    console.log('unknown file type:', fileType);
    fileContainer.innerHTML = 'Cannot display this file type. Please download the file to view it: <a href="' + filePath + '">Download file</a>';
  }
}