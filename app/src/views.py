import streamlit as st
import altair as alt

def render_data_insights(global_stats, user_stats, cluster_data, book_stats):
    """
    Renders the Data Insights dashboard.
    """
    st.title("Data Insights & Analytics")
    
    # 1. Global KPIs
    st.header("Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", global_stats["Total Users"])
    with col2:
        st.metric("Library Size", global_stats["Total Books in Library"])
    with col3:
        st.metric("Total Borrows", global_stats["Total Borrows"])
    with col4:
        st.metric("Reborrow Rate", f"{global_stats['Reborrow Rate']:.2f}%")
        
    st.markdown("---")
    
    # 2. Visualization (Clustering)
    st.header("Book Clustering (By Category)")
    st.caption("Visualizing book distribution. Points are grouped by category to simulate vector clusters.")
    
    chart = alt.Chart(cluster_data).mark_circle(size=60).encode(
        x=alt.X('x', axis=None),
        y=alt.Y('y', axis=None),
        color=alt.Color('Category_Grouped', legend=alt.Legend(title="Category")),
        tooltip=['Title', 'Author', 'Main_Category']
    ).properties(
        width='container',
        height=500
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # 3. User Statistics
    st.header("User Activity Breakdown")
    st.dataframe(
        user_stats, 
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    
    # 4. Book Popularity
    st.header("Book Popularity Analytics")
    
    # Unpack book stats
    borrow_counts_df, top_books_df, top_categories_df = book_stats
    
    tab1, tab2, tab3 = st.tabs(["Top Books", "Top Categories", "All Books"])
    
    with tab1:
        st.subheader("Top 10 Most Borrowed Books")
        st.bar_chart(top_books_df.set_index("Title")["Borrow_Count"], color="#FF4B4B")
        
    with tab2:
        st.subheader("Most Popular Categories")
        st.bar_chart(top_categories_df.set_index("Category")["Total_Borrows"], color="#1C83E1")
        
    with tab3:
        st.subheader("Full Library Borrow Counts")
        st.dataframe(
            borrow_counts_df,
            use_container_width=True,
            hide_index=True
        )
