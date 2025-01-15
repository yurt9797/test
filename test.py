import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ssl
import plotly.express as px
import ssl
import certifi
from urllib.request import urlopen
from matplotlib.patches import Rectangle

ssl_context = ssl.create_default_context(cafile=certifi.where())

data = pd.read_csv(urlopen("https://raw.githubusercontent.com/YuryM97/Data-Science-Data/refs/heads/main/master.csv", context=ssl_context))

st.title("Global suicide data from 1985 to 2015")

st.dataframe(data.head())

#fig 1
st.subheader("Average number of suicides per 100k people per year")
st.markdown("Press play or drag the slider to see data from different years.")

by_country = data.groupby(["country", "year"])
suicides_100k = by_country["suicides/100k pop"].sum().reset_index()

avg_suicides = suicides_100k[["country", "suicides/100k pop"]].groupby(["country"])["suicides/100k pop"].mean().reset_index().sort_values("suicides/100k pop", ascending = False)

by_country_year = data.groupby(["country", "year"])["suicides/100k pop"].mean().reset_index().sort_values("year").reset_index().head(2305)
del by_country_year["index"]

fig = px.choropleth(
    by_country_year,
    locations="country",
    locationmode="country names",
    color="suicides/100k pop",
    color_continuous_scale="Reds",
    animation_frame="year",
    title="Average number of suicides per 100k people per year"
)

fig.update_layout(coloraxis_colorbar = dict(title = "Suicides/100k", ticks = "outside"))

st.plotly_chart(fig)

#fig 2
st.subheader("Total suicides by age each year")
st.markdown("Drag the two sliders to control the year range displayed.")
by_year = data[["year", "age", "suicides_no"]].groupby(["age", "year"]).sum().reset_index()
by_year["age"] = by_year["age"].replace("5-14 years", "0-14 years")
by_year = by_year.sort_values(["age", "year"]).reset_index()
del by_year["index"]
by_year.head()
by_year = by_year.pivot(index="year", columns="age", values="suicides_no").fillna(0).sort_index().head(31)
by_year = by_year.reset_index()

start_year = st.slider("Start year", 1985, 2014, 1985)
end_year = st.slider("End year", start_year, 2015, 2015)
by_year = by_year[(by_year["year"] >= start_year) & (by_year["year"] <= end_year)]

cumulative_values = by_year.cumsum(axis = 1)

fig, ax = plt.subplots()

colors = plt.cm.viridis(np.linspace(0, 1, len(by_year.columns)))

for i, age in enumerate(by_year.columns):
  if i == 0:
    ax.fill_between(by_year["year"], 0, cumulative_values[age], label=age, color=colors[i], alpha=0.7)
  else:
    ax.fill_between(by_year["year"], cumulative_values.iloc[:, i-1], cumulative_values[age], label=age, color=colors[i], alpha=0.7)

plt.gca().set_yticks(range(0, 400001, 50000))

plt.ylabel("Number of Suicides")
plt.xlabel("Year")
plt.title("Suicides by age group from 1985 to 2015")

plt.legend(loc = "upper left")

st.pyplot(fig)

#fig 3
st.subheader("Average number of suicides per 100k by gender each year")
by_gender = data[["year", "sex", "suicides/100k pop"]].groupby(["year", "sex"]).sum().reset_index().pivot(index = "year", columns = "sex", values = "suicides/100k pop").reset_index().head(31)

year = by_gender["year"]
male = by_gender["male"]
female = by_gender["female"] * -1

fig, ax = plt.subplots()

plt.bar(year, male, label = "Male Suicides", color = "blue")
plt.bar(year, female, label = "Female Suicides", color = "red")

plt.gca().set_yticks(range(-5000, 15001, 5000))
plt.gca().set_yticklabels([abs(y) for y in range(-5000, 15001, 5000)])

plt.axhline(0, color = "black", linewidth = 0.8)

plt.ylabel("Number of Suicides")
plt.xlabel("Year")
plt.title("Suicides by gender from 1985 to 2015")

plt.legend(loc = "upper right")

st.pyplot(fig)

#fig 4
st.subheader("Total makeup of suicide data by gender and age groups")
colors = ["#9ffc92", "#8fe384", "#81cf76", "#76bd6c", "#6aab61", "#5b9453"]

data["age"] = data["age"].replace("5-14 years", "0-14 years")

avg_suicides_year = data["suicides_no"].sum()/data["year"].nunique()

male_num = data[data["sex"] == "male"]["suicides_no"].sum()/data["year"].nunique()
female_num = data[data["sex"] == "female"]["suicides_no"].sum()/data["year"].nunique()

male_proportion = data[data["sex"] == "male"]["suicides_no"].sum()/data["suicides_no"].sum()
female_proportion = data[data["sex"] == "female"]["suicides_no"].sum()/data["suicides_no"].sum()

male_age_prop = data[data["sex"] == "male"].reset_index()[["age", "suicides_no"]].groupby("age").sum().reset_index().sort_values("age").set_index("age").T/data[data["sex"] == "male"]["suicides_no"].sum()
male_age_prop = male_age_prop.iloc[0].tolist()

male_age_num = data[data["sex"] == "male"].reset_index()[["age", "suicides_no"]].groupby("age").sum().reset_index().sort_values("age").set_index("age").T/data["year"].nunique()
male_age_num = male_age_num.iloc[0].tolist()

female_age_prop = data[data["sex"] == "female"].reset_index()[["age", "suicides_no"]].groupby("age").sum().reset_index().set_index("age").T/data[data["sex"] == "female"]["suicides_no"].sum()
female_age_prop = female_age_prop.iloc[0].tolist()

female_age_num = data[data["sex"] == "female"].reset_index()[["age", "suicides_no"]].groupby("age").sum().reset_index().sort_values("age").set_index("age").T/data["year"].nunique()
female_age_num = female_age_num.iloc[0].tolist()

age_groups = data[data["sex"] == "male"].reset_index()[["age", "suicides_no"]].groupby("age").sum().reset_index().sort_values("age")["age"].values

fig, ax = plt.subplots(figsize=(10, 6))

total_height = avg_suicides_year

ax.add_patch(Rectangle((0, 0), 1, total_height, color="orange", label="Total"))

male_height = total_height * male_proportion
female_height = total_height * female_proportion

ax.add_patch(Rectangle((1, 0), 1, male_height, color = "lightblue", label = "Male"))
ax.add_patch(Rectangle((1, male_height), 1, female_height, color = "pink", label = "Female"))

y_offset = 0
i = 0
for age in male_age_prop:
  height = male_height * age
  ax.add_patch(Rectangle((2, y_offset), 1, height, color = colors[i], label = age_groups[i]))
  ax.text(2.5, y_offset + height/2, f"{int(male_age_num[i])}", ha = "center", va = "center", fontsize = 7, color = "black")
  y_offset += height
  i += 1

y_offset = male_height
i = 0
height = 0.00
for age in female_age_prop:
  height = female_height * age
  ax.add_patch(Rectangle((2, y_offset), 1, height, color = colors[i]))
  ax.text(2.5, y_offset + height/2, f"{int(female_age_num[i])}", ha = "center", va = "center", fontsize = 7, color = "black")
  y_offset += height
  i += 1

ax.text(1/2, total_height/2, f"{int(avg_suicides_year)}", ha = "center", va = "center", fontsize = 20, color = "black")
ax.text(1.5, male_height/2, f"{int(male_num)}", ha = "center", va = "center", fontsize = 20, color = "black")
ax.text(1.5, male_height + female_height/2, f"{int(female_num)}", ha = "center", va = "center", fontsize = 20, color = "black")

ax.set_xlim(0, 3)
ax.set_ylim(-1, total_height)
ax.get_xaxis().set_visible(False)
plt.title("Average yearly suicides by sex and age groups")
plt.legend(loc = "upper left")

st.pyplot(fig)