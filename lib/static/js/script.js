var treeLinks = document.querySelectorAll('.tree-menu > li > a');
for (var i = 0; i < treeLinks.length; i++) {
  treeLinks[i].addEventListener('click', function(event) {
    event.preventDefault();
    this.parentNode.classList.toggle('active');
  });
}
