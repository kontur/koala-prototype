<html ng-app="Koala">
<head>

</head>
<body>

<a href="#/">Home</a>
<div ng-view>
   view
</div>


----
<h1>Debug links</h1>
<ul>
    <li><a href="/recent">User Recent Media</a> Calls user_recent_media - Get a list of a user"s most recent media</li>
    <li><a href="/user_media_feed">User Media Feed</a> Calls user_media_feed - Get the currently authenticated user"s
        media feed uses pagination
    </li>
    <li><a href="/location_recent_media">Location Recent Media</a> Calls location_recent_media - Get a list of recent
        media at a given location, in this case, the Instagram office
    </li>
    <li><a href="/media_search">Media Search</a> Calls media_search - Get a list of media close to a given latitude and
        longitude
    </li>
    <li><a href="/media_popular">Popular Media</a> Calls media_popular - Get a list of the overall most popular media
        items
    </li>
    <li><a href="/user_search">User Search</a> Calls user_search - Search for users on instagram, by name or username
    </li>
    <li><a href="/user_follows">User Follows</a> Get the followers of @instagram uses pagination</li>
    <li><a href="/location_search">Location Search</a> Calls location_search - Search for a location by lat/lng</li>
    <li><a href="/tag_search">Tags</a> Search for tags, view tag info and get media by tag</li>
</ul>
<img src="/static/img/yeoman.png">

<script src="/static/js/libs.js"></script>
<script src="/static/js/app.js"></script>
</body>
</html>