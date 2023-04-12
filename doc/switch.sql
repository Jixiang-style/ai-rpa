UPDATE landingbj.ld_rpa_app SET default_show=-1;
UPDATE landingbj.ld_rpa_app SET default_show=1 WHERE id IN (2, 3);
UPDATE landingbj.ld_rpa_app SET default_show=0 WHERE id IN (1, 7);

UPDATE landingbj.ld_rpa_app SET default_show=0;
UPDATE landingbj.ld_rpa_app SET default_show=1 WHERE id IN (2, 3, 4, 9);