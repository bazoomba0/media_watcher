(function(){
  const grid = document.getElementById('grid');
  const mediaPathEl = document.getElementById('mediaPath');
  const deleteOnViewEl = document.getElementById('deleteOnView');
  const trashBtn = document.getElementById('trashBtn');
  const trashCountEl = document.getElementById('trashCount');
  const trashModal = document.getElementById('trashModal');
  const markedListEl = document.getElementById('markedList');
  const markedCountEl = document.getElementById('markedCount');
  const undoBtn = document.getElementById('undoBtn');
  const markAllBtn = document.getElementById('markAll');
  const downloadBash = document.getElementById('downloadBash');
  const downloadWin = document.getElementById('downloadWin');
  const copyScript = document.getElementById('copyScript');
  const closeTrash = document.getElementById('closeTrash');

  mediaPathEl.textContent = 'Media: ' + MEDIA_ROOT;

  const state = {
    marked: new Set(),
    lastMarked: null,
    undoTimer: null
  };

  function updateTrashCount(){
    const n = state.marked.size;
    if(n>0){
      trashCountEl.style.display='inline-block';
      trashCountEl.textContent = n;
    } else {
      trashCountEl.style.display='none';
    }
  }

  function renderGrid(){
    grid.innerHTML = '';
    FILE_LIST.forEach(function(rel){
      const card = document.createElement('div');
      card.className = 'card';

      const thumb = document.createElement('div');
      thumb.className = 'thumb';
      const fullPath = (MEDIA_ROOT.replace(/\/+$,'') + '/' + rel).replace(/\/+/g,'/');

      // image preview for common image types
      if(/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(rel)){
        const img = document.createElement('img');
        img.src = fullPath;
        img.className = 'thumb';
        img.alt = rel;
        img.loading = 'lazy';
        thumb.appendChild(img);
      } else {
        thumb.textContent = rel.split('/').slice(-1)[0];
      }

      const meta = document.createElement('div');
      meta.className = 'meta';

      const label = document.createElement('div');
      label.textContent = rel;
      label.style.overflow='hidden';
      label.style.textOverflow='ellipsis';
      label.style.whiteSpace='nowrap';
      label.style.maxWidth='60%';

      const controls = document.createElement('div');

      const viewBtn = document.createElement('button');
      viewBtn.textContent = 'View';
      viewBtn.onclick = function(){
        // open in new tab/window
        window.open(fullPath, '_blank');
        if(deleteOnViewEl.checked){
          markForDeletion(rel);
        }
      };

      const chk = document.createElement('input');
      chk.type='checkbox';
      chk.checked = state.marked.has(rel);
      chk.onchange = function(){
        if(chk.checked) state.marked.add(rel); else state.marked.delete(rel);
        updateTrashCount();
      };

      controls.appendChild(viewBtn);
      controls.appendChild(chk);

      meta.appendChild(label);
      meta.appendChild(controls);

      card.appendChild(thumb);
      card.appendChild(meta);

      grid.appendChild(card);
    });
    updateTrashCount();
  }

  function markForDeletion(rel){
    state.marked.add(rel);
    state.lastMarked = rel;
    updateTrashCount();
    showUndo();
  }

  function showUndo(){
    undoBtn.style.display='block';
    if(state.undoTimer) clearTimeout(state.undoTimer);
    state.undoTimer = setTimeout(function(){
      // expire undo
      state.lastMarked = null;
      undoBtn.style.display='none';
      state.undoTimer = null;
      renderGrid();
    }, 5000);
    renderGrid();
  }

  undoBtn.onclick = function(){
    if(state.lastMarked && state.marked.has(state.lastMarked)){
      state.marked.delete(state.lastMarked);
      state.lastMarked = null;
      if(state.undoTimer) clearTimeout(state.undoTimer);
      undoBtn.style.display='none';
      renderGrid();
    }
  };

  trashBtn.onclick = function(){
    // show modal and list marked files
    populateMarkedList();
    trashModal.style.display='flex';
  };

  closeTrash.onclick = function(){trashModal.style.display='none'};

  function populateMarkedList(){
    markedListEl.innerHTML='';
    const arr = Array.from(state.marked);
    markedCountEl.textContent = arr.length;
    if(arr.length===0){
      markedListEl.textContent='No files marked for deletion.';
      return;
    }
    arr.forEach(function(rel){
      const row = document.createElement('div');
      row.style.display='flex';
      row.style.justifyContent='space-between';
      row.style.padding='6px 0';
      const name = document.createElement('div');
      name.textContent = rel;
      const unmark = document.createElement('button');
      unmark.textContent='Unmark';
      unmark.onclick = function(){ state.marked.delete(rel); updateTrashCount(); populateMarkedList(); renderGrid(); };
      row.appendChild(name);
      row.appendChild(unmark);
      markedListEl.appendChild(row);
    });
  }

  markAllBtn.onclick = function(){
    FILE_LIST.forEach(f=>state.marked.add(f));
    updateTrashCount();
    renderGrid();
  };

  function buildBashScript(){
    const lines = ['#!/bin/sh','# Delete script generated by media_watcher',''];
    Array.from(state.marked).forEach(rel=>{
      const p = (MEDIA_ROOT.replace(/\\/+$/,'') + '/' + rel).replace(/\\/g,'/');
      lines.push('rm -v -- "' + p.replace(/"/g,'\"') + '"');
    });
    return lines.join('\n') + '\n';
  }

  function buildWinScript(){
    const lines = ['@echo off','rem Delete script generated by media_watcher',''];
    Array.from(state.marked).forEach(rel=>{
      const p = (MEDIA_ROOT.replace(/\\/+$/,'') + '\\' + rel).replace(/\\/g,'\\\\');
      lines.push('del /f /q "' + p + '"');
    });
    return lines.join('\r\n') + '\r\n';
  }

  function download(filename, content){
    const blob = new Blob([content],{type:'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  downloadBash.onclick = function(){ download('delete_marked.sh', buildBashScript()); };
  downloadWin.onclick = function(){ download('delete_marked.bat', buildWinScript()); };
  copyScript.onclick = function(){ navigator.clipboard.writeText(buildBashScript()); alert('Bash delete script copied to clipboard'); };

  // initial render
  renderGrid();
})();
