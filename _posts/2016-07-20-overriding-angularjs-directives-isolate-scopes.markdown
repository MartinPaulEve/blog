---
title: "Overriding AngularJS directives' isolate scopes"
layout: post
image: 
    feature: geek.png
doi: "https://doi.org/10.59348/8kmyx-jg122"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/07/20/overriding-angularjs-directives-isolate-scopes"
---
We have a third-party Angular app and want to override the isolate scopes that are provided by its directives. We don't want to modify the original app. How can we do this? We use a decorator in our app controller to specify that only the code in the local app should be run. I'm pretty new to Angular, so there's probably some mistakes in the below terminology, but this works...

Take the following for example:

        app.decorator(
            "topBarDirective",
            function topBarDirectiveDecorator( $delegate ) {
                return( [ $delegate[1] ] );
            }
        );

What this does is to intercept the call to the "topBar" directive and returns only the second function in the list of directive delegates to be executed instead. Provided that the local copy of topBar is set at a lower priority than the "master" topBar, it will always be at index 1 in the delegate list.

In this way, we can modify the scope provided to the topBar directive in the normal way inside it.




