-- ranks the country origins of bands

SELECT origin, SUM(fans) as nb_fans
FROM hbtn_0d_tvshows.metal_bands
GROUP BY origin
ORDER BY nb_fans;
