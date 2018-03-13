/*********/
/* state */
/*********/
var classIds = [];
var currentClass = {id: null, title: null, description: null};
var classInfo = {
  combined: null,
  ascii: null,
  tokenised: null,
  stemmed: null,
  indices: null,
};
var recommendations = [];
var nRecommendations = 5;

/************/
/* requests */
/************/

/****************/
/* TO MODIFY!!! */
/****************/

function getClassData(classId, callback) {

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
  let response = JSON.parse(this.responseText);
  callback(response.id, response.title, response.description);
  }
  else if (this.readyState == 4 && this.status == 400) {
  showError(this.responseText);
  }
  };
  url = "/courses/" + classId
  xhttp.open('GET', url, true); // définir url
  xhttp.send();
}

function getClassInfo(classId, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
  let response = JSON.parse(this.responseText);
  callback(response.combined, response.ascii, response.tokenised, response.stemmed, response.indices);
  }
  //combined titre+descrition en une seule srting  ascii idem, tokenised : list des mots de combines  stemmed : stem(tokenised), indices : de la matrice tfidf
  else if (this.readyState == 4 && this.status == 400) {
  showError(this.responseText);
  }
  };
  url = "/courses/" + classId
  xhttp.open('GET', url, true);
  xhttp.send();
}

function getRecommendations(classId, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
  let response = JSON.parse(this.responseText);
  callback(response.recommendationsData);
  }
  else if (this.readyState == 4 && this.status == 400) {
  showError(this.responseText);
  }
  };
  url = "/courses/" + classId
  xhttp.open('GET', url, true); // définir url
  xhttp.send();
}

/******************/
/* view functions */
/******************/

function newClassView(id, title, description, similarity) {
  let recommender = document.getElementById('recommender');

  let foldableDiv = document.createElement('div');

  let titleDiv = document.createElement('div');
  let descriptionDiv = document.createElement('div');

  let titleIdDiv = document.createElement('div');
  let titleTitleDiv = document.createElement('div');
  let titleSimilarityDiv = document.createElement('div');

  foldableDiv.className = 'foldable';
  titleDiv.className = 'title';
  descriptionDiv.className = 'description';

  titleIdDiv.innerHTML = id.toUpperCase();
  titleTitleDiv.innerHTML = title;
  titleSimilarityDiv.innerHTML = '(' + similarity.toFixed(3) + ')';
  descriptionDiv.innerHTML = description;

  let divs = recommender.getElementsByTagName('div');
  recommender.insertBefore(foldableDiv, divs[divs.length - 1]);
  foldableDiv.appendChild(titleDiv);
  foldableDiv.appendChild(descriptionDiv);
  titleDiv.appendChild(titleIdDiv);
  titleDiv.appendChild(titleTitleDiv);
  titleDiv.appendChild(titleSimilarityDiv);

  foldableDiv.addEventListener('click', e => showDescription(e));
}

function modifyClassView(class_, id, title, description, similarity) {
  let titleDiv = class_.getElementsByClassName('title')[0];
  let descriptionDiv = class_.getElementsByClassName('description')[0];
  titleDiv.getElementsByTagName('div')[0].innerHTML = id.toUpperCase();
  titleDiv.getElementsByTagName('div')[1].innerHTML = title;
  titleDiv.getElementsByTagName('div')[2].innerHTML =
    '(' + similarity.toFixed(3) + ')';
  descriptionDiv.innerHTML = description;
}

function mainClassDataView() {
  let searchedClass = document.getElementById('searched-class');
  let title = searchedClass.getElementsByClassName('title')[0];
  let description = searchedClass.getElementsByClassName('description')[0];
  let titleDivs = title.getElementsByTagName('div');
  if (titleDivs.length === 0) {
    title.appendChild(document.createElement('div'));
    title.appendChild(document.createElement('div'));
    titleDivs = title.getElementsByTagName('div');
  }
  titleDivs[0].innerHTML = currentClass.id.toUpperCase();
  titleDivs[1].innerHTML = currentClass.title;
  description.innerHTML = currentClass.description;
  document.getElementById('user-input').value = '';
  searchedClass.style.visibility = 'visible';
}

function mainClassInfoView() {
  document.getElementById('combined').innerHTML = classInfo.combined;
  document.getElementById('ascii').innerHTML = classInfo.ascii;
  document.getElementById('tokenised').innerHTML = classInfo.tokenised.join(
    ', ',
  );
  document.getElementById('stemmed').innerHTML = classInfo.stemmed.join(', ');
  document.getElementById('indices').innerHTML = classInfo.indices.join(', ');

  let tabs = document.getElementsByClassName('tab');
  let contents = document.getElementsByClassName('content');
  if (
    tabs[1].className == 'tab active-tab' &&
    contents[1].className == 'content hidden-content'
  ) {
    contents[1].className = 'content';
  }
}

function recommendationsView() {
  let recommender = document.getElementById('recommender');
  let currentClasses = recommender.getElementsByClassName('foldable');
  let i = 0;
  for (; i < recommendations.length; i++) {
    let r = recommendations[i];
    if (i < currentClasses.length) {
      modifyClassView(
        currentClasses[i],
        r.id,
        r.title,
        r.description,
        r.similarity,
      );
    } else {
      newClassView(r.id, r.title, r.description, r.similarity);
    }
  }
  if (currentClasses.length >= i) {
    for (; i < currentClasses.length; i++) {
      recommender.removeChild(recommender.childNodes[i]);
    }
  }
  let tabs = document.getElementsByClassName('tab');
  let contents = document.getElementsByClassName('content');
  if (
    tabs[0].className == 'tab active-tab' &&
    contents[0].className == 'content hidden-content'
  ) {
    contents[0].className = 'content';
  }
}

function showError(error) {
  console.log(error);
  document.getElementById('user-input').style.border = '1px solid #990000';
}

/********************/
/* update functions */
/********************/

function changeMainClass() {
  nRecommendations = 5;
  let classId = document.getElementById('user-input').value.toLowerCase();
  let searchedClass = document.getElementById('searched-class');
  getClassData(classId, updateMainClass);
  getClassInfo(classId, updateMainClassInfo);
  getRecommendations(classId, updateRecommendations);
}

function updateMainClass(id, title, description) {
  currentClass = {id: id, title: title, description: description};
  mainClassDataView(id, title, description);
}

function updateMainClassInfo(combined, ascii, tokenised, stemmed, indices) { // Appel des requêtes
  classInfo = {
    combined: combined,
    ascii: ascii,
    tokenised: tokenised,
    stemmed: stemmed,
    indices: indices,
  };
  mainClassInfoView();
}

function updateRecommendations(recommendationsData) {
  recommendations = recommendationsData;
  recommendationsView();
}

function showDescription(element) {
  let description = element.currentTarget.getElementsByClassName(
    'description',
  )[0];
  let title = element.currentTarget.getElementsByClassName('title')[0];
  if (description.className == 'description description-shown') {
    description.className = 'description';
    title.className = 'title';
  } else {
    description.className = 'description description-shown';
    title.className = 'title title-shown';
  }
}

function changeTab() {
  let tabs = document.getElementsByClassName('tab');
  let contents = document.getElementsByClassName('content');
  if (tabs[0].className == 'tab active-tab') {
    tabs[0].className = 'tab';
    tabs[1].className = 'tab active-tab';
    if (currentClass.id) {
      contents[0].className = 'content hidden-content';
      contents[1].className = 'content';
    }
  } else {
    tabs[0].className = 'tab active-tab';
    tabs[1].className = 'tab';
    if (currentClass.id) {
      contents[0].className = 'content';
      contents[1].className = 'content hidden-content';
    }
  }
}

function addRecommendation() {
  nRecommendations = nRecommendations + 1;
  let classId = currentClass.id;
  getRecommendations(classId, updateRecommendations);
}

document.addEventListener('DOMContentLoaded', function() {
  document
    .getElementById('user-input')
    .addEventListener('keypress', function(e) {
      document.getElementById('user-input').style.border = '1px solid #d3d4df';
      if (e.keyCode == 13) {
        changeMainClass();
      }
    });
  Array.from(document.getElementsByClassName('foldable')).map(x =>
    x.addEventListener('click', e => showDescription(e)),
  );
  document.getElementById('tabs').addEventListener('click', () => changeTab());
  document
    .getElementById('add-recommendation')
    .addEventListener('click', () => addRecommendation());
});
