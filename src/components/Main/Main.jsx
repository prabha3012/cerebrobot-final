import React ,{useContext} from 'react'
import './Main.css'
import { assets } from '../../assets/assets'
import { Context } from '../../context/Context'

const Main = () => {

  const {onSent,recentPrompt,showResult,loading,resultData,setInput,input}=useContext(Context);
  return (
    <div className='main'>
      <div className="nav">
        <p>CereBroBot</p>
        
      </div>
      <div className="main-container">

        {!showResult
        ?<>
        <div className="greet">
          <p><span>Hello, Developer.</span></p>
          <p>How can I help you?</p>
        </div>
        
        </>
        : <div className='result'>
            <div className="result-title">
              <img src={assets.user_icon} alt="" />
              <p>{recentPrompt}</p>
            </div>
            <div className="result-data">
              <img src={assets.CereBroBot_icon} alt="" />
              {loading?
                <div className="loader">
                  <hr />
                  <hr />
                  <hr />
                </div>
  
              :<p dangerouslySetInnerHTML={{ __html: resultData || "<i>No response found.</i>" }} />
              }      
            </div>
        </div>
        }

        

        <div className="main-bottom">
          <div className="search-box">
            <input onChange={(e)=>setInput(e.target.value)} value={input} type="text" placeholder='Enter a prompt here' />
            <div>
              
              {input?<img onClick={()=>onSent(input)} src={assets.send_icon} alt="" />:null}
            </div>
          </div>
          <p className="bottom-info">CereBroBot may display inaccurate info, including about people, so double-check its responses. Yout privacy and CereBroBot Apps</p>
        </div>
      </div>
    </div>
  )
}

export default Main