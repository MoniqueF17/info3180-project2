/* Add your Application JavaScript */
/*global Vue*/
/*global VueRouter*/
/*global fetch*/

Vue.component('app-header', {
    template: `
      <nav class="navbar navbar-inverse navbar-fixed-top navbar-light" style="background-color: #5a90dc;">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="{{ url_for('home') }}"><img src="{{ url_for('static',filename="header_logo.png") }}" height="30px" width="110px"></a>
        </div>
        
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav navbar-right">
            {% if not current_user.is_authenticated %}
                <li class="active"><a href="{{ url_for('home') }}">Home</a></li>
            {% else %}
                <li class="active"><a href="{{ url_for('logout') }}">Logout</a></li>
            {% endif %}
                
              <li {%- if request.path == "/addItem" %} class="active"{% endif %}>
              <a href="{{ url_for('home') }}">Explore</a>
              </li>
              <li {%- if request.path == "/profile/" %} class="active"{% endif %}>
              <a href="{{ url_for('profile') }}">My Profile</a>
              </li>
              
              <!--SHOULD BE MOVE-->
              <li {%- if request.path == "/posts/new" %} class="active"{% endif %}>
              <a href="{{ url_for('addPost') }}">New Post</a>
              </li>
            
              <li class="active"><a href="{{ url_for('about') }}">About</a></li>
          </ul>
        </div><!--/.nav-collapse -->
    </div>
</nav>
    `,
    data: function() {}
});


Vue.component('app-footer', {
    template: `
        <footer>
            <div class="container">
                <p>Copyright &copy {{ year }} Flask Inc.</p>
            </div>
        </footer>
    `,
    data: function() {
        return {
            year: (new Date).getFullYear()
        };
    }
});


const Explore = Vue.component('explore', {
  template: `
    <div class="row">
      <div class="col-md-7 ml-5 mr-5 border bg-white rounded" v-for="post in posts">
        <div class="postcard">
          <div class="postcard-header pl-4 bg-white">
            <h5 class="postcard-title"> <img v-bind:src=post.user_photo alt="User Profile Photo"/> {{ post.username }}</h5>
          </div>
          <li class="list-group-item no-padding">
            <img v-bind:src=post.photo class="postcard-img-top" alt="Picture posted by user">
          </li>
          <div class="postcard-body text-muted">
            <small>{{ post.caption }}</small>
          </div>
          <div class="postcard-footer">
            <footer>
              <i class="fas fa-heart d-inline-block"></i>
              {{ post.likes }}
              Likes
            </footer>
            <footer>{{ post.created_on }}</footer>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <router-link to="/posts/new"><input type="submit" value="Submit" class="btn btn-primary btn-block"></router-link>
      </div>
    </div>
  `,
  created: function(){
    let self = this;
    
    fetch("/api/posts", {
      method: 'GET',
      headers:{
        'Authorization': `Bearer ${localStorage.token}`,
        'X-CSRFToken': token
      },
      credentials: 'same-origin'
    })
    .then(function(response){
      return response.json();
    })
    .then(function(jsonResponse){
      console.log(jsonResponse);
      if(jsonResponse.hasOwnProperty("code")){
        router.replace('/login');
      }
      else{
        if(jsonResponse.hasOwnProperty("posts")){
          if(jsonResponse.posts.length !=0){
            console.log("Posts: "+jsonResponse.posts);
            self.posts = jsonResponse.posts.reverse();
          }
          else{
            self.valid = true;
            self.message = 'No posts to be displayed';
          }
        }
      }
    }).catch(function(error){
      console.log(error);
    });
  },
  data: function(){
    return {
      posts: [],
      message: '',
      valid: false
    }
  }
});


const Home = Vue.component('home', {
  template: `
    <div class="flex-container">
    <div id="img">
        <img src="{{ url_for('static',filename="img_forest.jpg") }}">
    </div>
    
    <div id="word">
        <div>
           <h1 class="page-header"><img src="{{ url_for('static',filename="home_logo.png") }}" height="40px" width="200px"></h1> 
        </div>
    
        <p class="message">Share photos of your favourite moments with friends, family and the world.</p></br></br></br>
        
        <div class="button">
            <button id="register-button"><a href="{{ url_for('register') }}" style="text-decoration:none;">Register</a></button>
            <button id="login-button"><a href="{{ url_for('login') }}" style="text-decoration:none;">Login</a></button>
        </div>
    </div>
</div>
  `,
  data: function() {
    return {}
  }
});


const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/', component: Home},
    { path: '/register', component: Register},
    { path: '/login', component: Login},
    { path: "/explore", component: Explore}
  ]
});


let app = new Vue({
    el: '#app',
    router
});