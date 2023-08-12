async function renderReplies(id){
    console.log(id);

    const repliesList = document.querySelector('.replies');

    const replyTree = await fetch(`/api/repliesforpost/${id}`).then(x => x.json());

    // we don't render 0 because that's the post we're replying to
    for(let i = 1; i < replyTree.length; i++){
        const tree = replyTree[i];
        recursivelyRender(tree, repliesList);
    }
    
}

// tree is an array and at is a ul node
function recursivelyRender(tree, at, depth=0){
    //first elem will be the reply itself; following elems will be replies to the reply
    //the second elem of the reply is the body
    if(depth > 50){
        console.error('Too much recursion, something broke', tree, at);
        throw 'Too much recursion (over 50 layers deep) at recursivelyRender, something broke';
    }

    for(let i = 0; i < tree.length; i++){
        const li = document.createElement('li');

        //if there's no nesting to take care of (we're at the deepest level of nesting)
        if(typeof tree[i][0] === 'string' && typeof tree[i][1] === 'string'){
            li.innerText = tree[i][1]; // just set the li's text to the body of the reply
        }else{ // if there are replies to this reply
            const ul = document.createElement('ul'); // create a list to contain them
            li.appendChild(ul); // set that list as the contents of the li
            recursivelyRender(tree[i], ul, depth+1); //then render the replies to the reply
        }

        at.appendChild(li); // add the li to the "at" list
    }
}