
def get_book_css(width_vw, height_px):
    return f"""
    /* GLOBAL */
    html, body {{
      margin: 0;
      padding: 0;
      height: 100%;
      width: 100%;
      background: #0f172a;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* BOOK CONTAINER */
    .book {{
      position: relative;
      width: {width_vw}vw; 
      height: {height_px}px;
      perspective: 2500px;
      transform-style: preserve-3d;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    
    /* PAGES CONTAINER */
    .pages {{
      position: relative;
      width: 100%;
      height: 100%;
      transform-style: preserve-3d;
    }}
    
    /* COMMON PAGE STYLES */
    .page {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 50%;
      height: 100%;
      background: #fdfaf5;
      box-sizing: border-box;
      border: 1px solid #d1d5db;
      display: flex;
      flex-direction: column;
      padding: 40px;
      overflow: hidden;
    }}
    
    /* LEFTS & RIGHTS */
    .page-left {{
      left: 0;
      border-radius: 5px 0 0 5px;
      background: linear-gradient(to right, #e5e5e5 0%, #fdfaf5 20%, #fdfaf5 100%);
      z-index: 1;
      opacity: 0;
      transition: opacity 0.5s ease-in-out;
    }}
    .book.open .page-left {{
      z-index: 25;
    }}
    .page-right {{
      right: 0;
      border-radius: 0 5px 5px 0;
      background: linear-gradient(to left, #e5e5e5 0%, #fdfaf5 20%, #fdfaf5 100%);
      z-index: 1; 
    }}
    
    /* CONTENT */
    .content-container {{
      opacity: 1;
      transition: opacity 0.4s ease-in-out;
      height: 100%;
      display: flex;
      flex-direction: column;
    }}
    .content-container.fade-out {{
      opacity: 0;
    }}
    
    /* SCROLLABLE */
    .scrollable-content {{
        flex: 1;
        overflow-y: auto;
        padding-right: 10px;
        margin-top: 10px;
    }}
    .scrollable-content::-webkit-scrollbar {{
      width: 6px;
    }}
    .scrollable-content::-webkit-scrollbar-track {{
      background: #f1f1f1; 
    }}
    .scrollable-content::-webkit-scrollbar-thumb {{
      background: #cbd5e1; 
      border-radius: 3px;
    }}
    .scrollable-content::-webkit-scrollbar-thumb:hover {{
      background: #94a3b8; 
    }}
    
    h2 {{
      margin-top: 0;
      font-size: 1.8rem;
      color: #374151;
      font-family: serif;
      border-bottom: 2px solid #e5e7eb;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }}
    p {{
      line-height: 1.6;
      color: #4b5563;
      font-size: 1rem;
    }}
    
    /* LIST ITEMS */
    .book-item {{
        background: #fff;
        border: 1px solid #e2e8f0;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .book-title {{
        font-weight: 600;
        color: #1e293b;
        font-size: 0.95rem;
    }}
    .book-author {{
        font-size: 0.85rem;
        color: #64748b;
        font-style: italic;
    }}

    /* COVER FRONT */
    .cover-front {{
      position: absolute;
      right: 0; 
      width: 50%;
      height: 100%;
      background: #1e293b;
      border: 4px solid #334155;
      border-left: 2px solid #475569; 
      border-radius: 0 8px 8px 0;
      transform-origin: left center;
      transform: rotateY(0deg);
      transition: transform 1.2s cubic-bezier(0.645, 0.045, 0.355, 1);
      z-index: 20;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      color: #f1f5f9;
      text-align: center;
      backface-visibility: hidden;
    }}
    .cover-title {{
      font-family: serif;
      font-size: 2.5rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 0.5rem;
    }}
    .cover-subtitle {{
      font-size: 1rem;
      color: #cbd5e1;
      font-style: italic;
    }}
    
    /* BUTTONS */
    .start-btn {{
      margin-top: 40px;
      padding: 12px 32px;
      border-radius: 999px;
      border: none;
      background: #f59e0b;
      color: #fff;
      font-weight: bold;
      font-size: 1.1rem;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .start-btn:hover {{
      transform: scale(1.05);
      box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6);
    }}
    
    .nav-buttons {{
      margin-top: auto; 
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      padding-top: 20px;
      border-top: 1px dashed #e5e7eb;
    }}
    .nav-btn {{
      padding: 8px 16px;
      border-radius: 6px;
      border: 1px solid #d1d5db;
      background: white;
      color: #374151;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .nav-btn:hover {{
      background: #f3f4f6;
      border-color: #9ca3af;
    }}

    /* OTHER LAYERS */
    .cover-inner {{
      position: absolute;
      width: 50%;
      height: 100%;
      right: 0;
      background: #334155;
      border-radius: 8px 0 0 8px;
      transform-origin: left center;
      transform: rotateY(0deg); 
      z-index: 19; 
      pointer-events: none; 
      transition: transform 1.2s cubic-bezier(0.645, 0.045, 0.355, 1);
    }}
    .flyleaf {{
      position: absolute;
      right: 0;
      width: 50%;
      height: 100%;
      background: #fff;
      border: 1px solid #e5e5e5;
      border-radius: 0 5px 5px 0;
      transform-origin: left center;
      transform: rotateY(0deg);
      z-index: 18;
      transition: transform 1.4s cubic-bezier(0.645, 0.045, 0.355, 1);
    }}
    
    /* FLIP PAGE */
    .flip-page {{
      position: absolute;
      right: 0;
      width: 50%;
      height: 100%;
      background: #fdfaf5;
      border: 1px solid #d1d5db;
      border-radius: 0 5px 5px 0;
      transform-origin: left center;
      transform-style: preserve-3d;
      z-index: 10; 
      display: none; 
    }}
    .flip-face {{
      position: absolute;
      inset: 0;
      backface-visibility: hidden;
      padding: 40px;
      box-sizing: border-box;
      background-color: #fdfaf5;
    }}
    .flip-front {{
      background: linear-gradient(to left, #e5e5e5 0%, #fdfaf5 15%, #fdfaf5 100%);
      border-radius: 0 5px 5px 0;
    }}
    .flip-back {{
      transform: rotateY(180deg);
      background: linear-gradient(to right, #e5e5e5 0%, #fdfaf5 15%, #fdfaf5 100%);
      border-radius: 5px 0 0 5px;
    }}

    /* USER SELECT */
    .user-select-container {{
        margin-top: 20px;
    }}
    select {{
        padding: 10px;
        font-size: 1rem;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 100%;
        margin-bottom: 20px;
        font-family: inherit;
    }}

    /* ANIMATIONS */
    @keyframes flipToLeft {{
      0% {{ transform: rotateY(0deg); }}
      100% {{ transform: rotateY(-180deg); }}
    }}
    @keyframes flipToRight {{
      0% {{ transform: rotateY(-180deg); }}
      100% {{ transform: rotateY(0deg); }}
    }}
    
    /* OPEN STATES */
    .book.open .cover-front {{
      transform: rotateY(-180deg);
      z-index: 1; 
    }}
    .book.open .cover-inner {{
      transform: rotateY(-180deg); 
      z-index: 20; 
    }}
    .book.open .flyleaf {{
      transform: rotateY(-178deg);
      z-index: 5;
    }}
    """
