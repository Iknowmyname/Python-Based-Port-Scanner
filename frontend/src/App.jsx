import React, {useState} from 'react'
import axios from 'axios'

export default function App(){
  const [banner, setBanner] = useState('')
  const [res, setRes] = useState(null)

  async function submit(){
    try{
      const r = await axios.get('http://localhost:8000/predict_banner', { params: { banner }})
      setRes(r.data)
    }catch(e){
      setRes({error: e.toString()})
    }
  }

  return (
    <div style={{padding:32}}>
      <h2>NetSense demo</h2>
      <textarea value={banner} onChange={e=>setBanner(e.target.value)} rows={6} cols={80} />
      <br/>
      <button onClick={submit}>Predict service</button>
      <pre>{JSON.stringify(res, null, 2)}</pre>
    </div>
  )
}
