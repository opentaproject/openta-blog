        
	function add_option_listener() {
          const checkboxButtons = document.querySelectorAll('input[name="option"]');
          checkboxButtons.forEach((checkbox) => {
              checkbox.addEventListener('change', () => {
                 hideshow(  checkbox.value );
             });
	  });
	}

	function make_hidden_block( pb, selector ){ 
	var elements = document.getElementsByClassName( "visible post " + pb  );
        if ( selector ){
	for (var i = 0; i < elements.length; i++) {
            elements[i].classList.add('hidden') ; // Do something with each element
	  }
        } else {
	for (var i = 0; i < elements.length; i++) {
	    elements[i].classList.remove('hidden') ; // Do something with each element
	  }


        }
        }


        function add_listener(){
          const checkboxBlockButtons =  document.querySelectorAll('input[type="checkbox"][class="pblock"]')
          checkboxBlockButtons.forEach((checkbox) => {
                checkbox.addEventListener('change', () => {
		    make_hidden_block( checkbox.id, checkbox.checked)
                });
	    });
	  }



        function count_visible() {
	    var posts =  document.getElementsByClassName('visible post');
            var blockdivs =  document.getElementsByClassName('pblock');
            for ( var i =0 ; i < blockdivs.length ; i++ ){ blockdivs[i].remove() }
            var count = 0
	    var bs = 3
            var isopen = false
            var isave = 0
            var bmax = Math.trunc( posts.length / bs )
            var ibeg = 0 
            for (var i = 0; i < posts.length; i++) {
                var d = posts[i].dataset.dateAttr
                var b =   count  / bs ;
                var c =  'pb_' + String( Math.trunc( b ) )
                   for( var k = 0 ; k < bmax ; k ++ ) {
                     posts[i].classList.remove('pb_' + String( k ) );
                     }
                    posts[i].classList.add(c)
                     
		if ( posts[i].checkVisibility() ) {
                      if ( count % bs == 0 || i == 0 ){
			var checkbox = document.createElement('input');
                        checkbox.type = 'checkbox'
			checkbox.classList.add('pblock')
                        var label = document.createElement('label');
                        label.innerHTML = '<span class="OpenTA-lhs-block">  begin_' + c + ' </span> - <span class="OpenTA-lhs-block"> ' + d  + ' </span>'
                        label.classList.add('pblock')
                        checkbox.id = c
                        posts[i].before( label)
                        label.prepend(checkbox)
                        var labelsave = label
                      



                        isopen = true
                        var csave = c
                        var isave = i
                    }
                    if ( count % bs == bs - 1   ){
			var db = document.createElement('div');
			db.textContent = '' // 'end_' + c + ' ' + d 
			db.classList.add('pblock')
                        posts[i].after(db)
                        isopen = false
                        // labelsave.innerHTML =  posts[i+1].dataset.dateAttr + '-' +    labelsave.innerHTML 
                        // labelsave.innerHTML =  re.sub(r'begin_[0-9]+',  posts[i+1].dataset.dateAttr + '-'
                        var isave = Math.min( i, posts.length-1)
                        labelsave.innerHTML = labelsave.innerHTML.replace(/begin_pb_\d+/ ,   posts[isave].dataset.dateAttr  )
                        
                    }
                    count ++ ;
		    isave = i
                }
              }

		if (  isopen ){
			var db = document.createElement('div');
			db.textContent = '' // 'end_' + c + ' ' + d 
			db.classList.add('pblock')
                        posts[isave].after(db)
                        var isave = posts.length-1
                        labelsave.innerHTML = labelsave.innerHTML.replace(/begin_pb_\d+/ ,   posts[isave].dataset.dateAttr  )

                        // labelsave.innerHTML = labelsave.innerHTML.replace(/begin_pb_\d+/ ,   posts[posts.length-1].dataset.dateAttr + ' -' )
 
	    }
            setTimeout(() => { add_listener(); }, 0);
            setTimeout(() => { collapse_boxes(); }, 0);
            return posts
        }


        function make_hidden( posts ){ for (var i = 0; i < posts.length; i++) {
            posts[i].classList.remove('visible') ; // Do something with each element
            posts[i].classList.add('hidden') ; // Do something with each element
        }
            return posts
        }

        function make_visible( posts ){ for (var i = 0; i < posts.length; i++) {
            posts[i].classList.remove('hidden') ; // Do something with each element
            posts[i].classList.add('visible') ; // Do something with each element
        }
            return posts
        }
        function hideshow( a ) {
	    var blockdivs =  document.getElementsByClassName('pblock');
            for ( var i =0 ; i < blockdivs.length ; i++ ){ blockdivs[i].remove() }
            var posts =  document.getElementsByClassName('post');
            var ckall =  document.getElementById('All')
            var ck = ckall.checked
            posts = make_hidden( posts )
            var checkedboxes = document.querySelectorAll('input[name="option"]:checked');
            console.log("CHECKEDFILTER = ", checkedboxes )
            var cpk = []; for ( var i = 0 ; i < checkedboxes.length ; i++ ){ cpk[i] = checkedboxes[i].id }
            console.log("CPK", cpk )
            

            if ( String(a) == 'All' ){
                const checkedboxes = document.querySelectorAll('input[name="option"]:checked');
                for ( let i = 0 ; i < checkedboxes.length ; i++ ){
                    checkedboxes[i].checked = false
                } document.getElementsByClassName('post hidden')
                ckall.checked = ck
                if (ck ){
                    posts = make_visible( posts )
                } else {
                    posts = make_hidden( posts )
                }
            } else {var posts =  document.getElementsByClassName('post');

                if (ck ){
                    posts = make_visible( posts )
                } else {
                    posts = make_hidden( posts )
                }
                try { var acopy = JSON.parse( a ); } catch (error ){ var acopy = a }
                const checkedboxes = document.querySelectorAll('input[name="option"]:checked');
                var ar = []
                var rid = []
                for ( let i = 0 ; i < checkedboxes.length ; i++ ){
                    if( checkedboxes[i].value != 'All'  ){
                        ar = ar.concat( JSON.parse(checkedboxes[i].value ) );
                        rid = rid.concat( [ checkedboxes[i].id  ] )
                    } document.getElementsByClassName('post hidden')
                } document.getElementsByClassName('post hidden')
                for (var i = 0; i < posts.length; i++) {
                    posts[i].classList.remove('visible') ; // Do something with each element
                    posts[i].classList.add('hidden') ; // Do something with each element
                }
		var posts =  document.getElementsByClassName('post');
                for ( let i = 0 ; i <  ar.length ; i++ ){ document.getElementById( 'post_' + String( ar[i] )   ).classList.replace('hidden','visible')  ; 
                  // console.log('post_' +  String( ar[i] ) ) 
                }
                const postchecks = document.getElementById( 'post_' + acopy[i] );
                var fk = document.getElementById("filter_key_selected"); if ( fk ) { fk.value = rid }
                ckall.checked = false;
            }
	    var blockdivs =  document.getElementsByClassName('pblock');
            for ( var i =0 ; i < blockdivs.length ; i++ ){ blockdivs[i].remove() }
            var checkedboxes = document.querySelectorAll('input[name="option"]:checked');
            console.log("CHECKEDFILTER = ", checkedboxes )
            var cpk = []; for ( var i = 0 ; i < checkedboxes.length ; i++ ){ cpk[i] = checkedboxes[i].id }
            console.log("CPK2", cpk )
            document.cookie = "filterkeys=" + JSON.stringify( cpk ) + ";path=/"



	    setTimeout(() => { count_visible(); }, 0);
            // setTimeout(() => { collapse_boxes(); }, 0);
	    return posts
        }

          function collapse_boxes() {
            const checkboxBlockButtons =  document.querySelectorAll('input[type="checkbox"][class="pblock"]');
	    checkboxBlockButtons.forEach((checkbox) => {
	        checkbox.checked = true;
	        checkbox.dispatchEvent(new Event("change"));
                          }

		    ); 
            var ck = document.querySelector('input[type="checkbox"][class="pblock"][id="pb_0"]' )
            if ( ck ){
            ck.checked = false
            ck.dispatchEvent( new Event( "change") )
            }
          }
