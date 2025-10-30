import { createContext, useEffect, useState } from "react";
import runChat from "../config/gemini";

export const Context = createContext();

const ContextProvider = (props) => {

    
    const [input,setInput]=useState("");
    const [recentPrompt,setRecentPrompt]=useState("");
    const [prevPrompts,setPrevPrompts]=useState([]);
    const [showResult,setShowResult]=useState(false);
    const [loading,setLoading]=useState(false);
    const [resultData,setResultData]=useState("");

    /* const onSent=async(prompt)=>{
        await runChat(input);
    } */

    const delayPara = (index,nextWord)=>{
        setTimeout(function(){
            setResultData(prev=>prev+nextWord);
        },75*index);
    }
    const newChat=()=>{
        setLoading(false);
        setShowResult(false);
        setRecentPrompt("");
        setResultData("");
        setInput("");

    }

    const onSent = async (prompt2) => {
        
        const prompt = typeof prompt2 === "string" ? prompt2 : "";
        if (!prompt.trim()) return;
        setResultData("");
        setLoading(true);
        setShowResult(true);
        
        
        try {
            let response;
            if(prompt2!==undefined){
                response=await runChat(prompt2);
                setRecentPrompt(prompt2);
            }else{
                setPrevPrompts(prev=>[...prev,prompt])
                setRecentPrompt(prompt);
                response=await runChat(prompt);
            }
            let responseArray = response.split("**");
            let newResponse="";
            for(let i=0;i<responseArray.length;i++){
                if(i%2===0){
                    newResponse+=responseArray[i];
                }else{
                    newResponse+="<b>"+responseArray[i]+"</b>";
                }
            }
            let newResponse2 = newResponse.split("*").join("</br>");
            let newResponseArray=newResponse2.split(" ");
            for(let i=0;i<newResponseArray.length;i++){
                const nextWord=newResponseArray[i];
                delayPara(i,nextWord+" ");
            }

            setInput("");
            setPrevPrompts((prev) => [prompt, ...prev]);
        } catch (error) {
            console.error("Chat Error:", error);
            setResultData("Sorry, something went wrong.");
        } finally {
            setLoading(false);
        }
    };

    
    /* useEffect(() => {
        const fetchData = async () => {
            await runChat(prompt);
        };
        fetchData();
    }, []); */
    useEffect(() => {
    onSent(prompt);
  }, []);

    const contextValue = {
        prevPrompts,
        setPrevPrompts,
        onSent,
        setRecentPrompt,
        recentPrompt,
        showResult,
        loading,
        resultData,
        input,
        setInput,
        newChat
    };

    return (
        <Context.Provider value={contextValue}>
            {props.children}
        </Context.Provider>
    );
};

export default ContextProvider;
