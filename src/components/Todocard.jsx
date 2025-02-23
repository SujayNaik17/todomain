import React from 'react'

export default function Todocard(props) {

    const {children,handledelete,index, handleedit} = props


  return (
    
      <li className='todoItem' >
        
        
        {children}
        <div className='actionsContainer'>
            <button onClick={()=> {
              handleedit(index)
            }}>
        <i class="fa-solid fa-pen-to-square"></i>
        </button>
        <button onClick={() =>{
          handledelete(index)
        }}>
        <i class="fa-solid fa-trash"></i>
        </button>
        </div>
        
        
        </li>
    
  )
}
