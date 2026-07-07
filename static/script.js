const dropZone=document.getElementById("dropZone");
const fileInput=document.getElementById("fileInput");
const fileName=document.getElementById("fileName");
const preview=document.getElementById("preview");
const uploadBtn=document.getElementById("uploadBtn");

let selectedFile=null;

dropZone.onclick=()=>fileInput.click();

dropZone.addEventListener("dragover",(e)=>{
e.preventDefault();
dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave",()=>{
dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop",(e)=>{
e.preventDefault();
dropZone.classList.remove("dragover");

if(e.dataTransfer.files.length){
handleFile(e.dataTransfer.files[0]);
}
});

fileInput.addEventListener("change",()=>{
if(fileInput.files.length){
handleFile(fileInput.files[0]);
}
});

function handleFile(file){

if(!file.type.startsWith("audio/")){
alert("Please select an audio file.");
return;
}

selectedFile=file;

fileName.innerHTML="Selected : "+file.name;

preview.src=URL.createObjectURL(file);

preview.style.display="block";

uploadBtn.disabled=false;
}

uploadBtn.onclick=async()=>{

if(!selectedFile) return;

uploadBtn.disabled=true;
uploadBtn.innerHTML="Processing...";

const formData=new FormData();

formData.append("audio",selectedFile);

try{

const response=await fetch("/process",{

method:"POST",

body:formData

});

if(!response.ok){

throw new Error("Processing Failed");

}

const blob=await response.blob();

const url=URL.createObjectURL(blob);

const a=document.createElement("a");

a.href=url;

a.download="cleaned_audio.wav";

document.body.appendChild(a);

a.click();

a.remove();

URL.revokeObjectURL(url);

uploadBtn.innerHTML="Completed ✔";

}
catch(e){

alert(e.message);

uploadBtn.innerHTML="Upload & Process";

}

uploadBtn.disabled=false;

}
